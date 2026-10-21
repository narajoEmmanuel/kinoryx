"""Reproducible digital filtering for exploratory gait signals.

The engine intentionally exposes a small, explicit subset of general signal
processing. Defaults preserve the original KINORYX demonstration (a 4th-order
6 Hz Butterworth low-pass applied forward and backward), while the public API
also supports linear-phase FIR and causal processing.
"""

from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
from scipy.signal import (
    butter,
    detrend as scipy_detrend,
    fftconvolve,
    firwin,
    freqz,
    iirnotch,
    sosfilt,
    sosfilt_zi,
    sosfiltfilt,
    sosfreqz,
    tf2sos,
)

FilterKind = Literal["lowpass", "highpass", "bandpass", "bandstop", "notch"]
FilterFamily = Literal["butterworth", "fir"]
DetrendMode = Literal["constant", "linear"]


@dataclass(frozen=True)
class FilterSpec:
    """Complete, serializable description of one filtering operation.

    Frequencies are always expressed in hertz. A tuple is required for
    band-pass and band-stop filters. FIR filters use an odd number of taps so
    their group delay is an integer number of samples.
    """

    kind: FilterKind = "lowpass"
    cutoff_hz: float | tuple[float, float] = 6.0
    family: FilterFamily = "butterworth"
    order: int = 4
    zero_phase: bool = True
    fir_numtaps: int | None = None
    fir_transition_hz: float | None = None
    notch_quality: float = 30.0
    detrend: DetrendMode | None = None


@dataclass(frozen=True)
class FilterReport:
    """Provenance needed to reproduce and review a filtered signal."""

    spec: FilterSpec
    sampling_hz: float
    implementation: str
    coefficient_form: Literal["sos", "fir"]
    coefficient_count: int
    effective_order: int
    segments: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class FilterResult:
    values: np.ndarray
    report: FilterReport


@dataclass(frozen=True)
class FrequencyResponse:
    frequency_hz: np.ndarray
    magnitude_db: np.ndarray


@dataclass(frozen=True)
class _DesignedFilter:
    spec: FilterSpec
    sampling_hz: float
    coefficients: np.ndarray
    form: Literal["sos", "fir"]


def _as_signal(values: np.ndarray) -> np.ndarray:
    signal = np.asarray(values, dtype=float)
    if signal.ndim != 1 or signal.size < 2:
        raise ValueError("Expected a one-dimensional signal with at least 2 samples")
    if not np.isfinite(signal).all():
        raise ValueError("Signal contains non-finite values")
    return signal


def _validate_sampling(sampling_hz: float) -> float:
    sampling_hz = float(sampling_hz)
    if not np.isfinite(sampling_hz) or sampling_hz <= 0:
        raise ValueError("Sampling frequency must be positive and finite")
    return sampling_hz


def _validated_cutoff(
    spec: FilterSpec, sampling_hz: float
) -> float | tuple[float, float]:
    nyquist = sampling_hz / 2
    if spec.kind in ("bandpass", "bandstop"):
        if not isinstance(spec.cutoff_hz, tuple) or len(spec.cutoff_hz) != 2:
            raise ValueError(f"{spec.kind} requires a (low, high) cutoff tuple")
        low, high = (float(value) for value in spec.cutoff_hz)
        if not (0 < low < high < nyquist):
            raise ValueError("Band edges must be ordered and below the Nyquist frequency")
        return low, high
    if isinstance(spec.cutoff_hz, tuple):
        raise ValueError(f"{spec.kind} requires one cutoff frequency")
    cutoff = float(spec.cutoff_hz)
    if not (0 < cutoff < nyquist):
        raise ValueError("Cutoff must lie below the Nyquist frequency")
    return cutoff


def _default_fir_transition(spec: FilterSpec, sampling_hz: float) -> float:
    cutoff = _validated_cutoff(spec, sampling_hz)
    critical = min(cutoff) if isinstance(cutoff, tuple) else cutoff
    # Restrained adaptation of EEGLAB's windowed-sinc transition heuristic.
    return min(2 * critical, 2.0) if critical <= 8 else critical * 0.25


def _default_fir_numtaps(spec: FilterSpec, sampling_hz: float) -> tuple[int, float]:
    transition = float(
        spec.fir_transition_hz
        if spec.fir_transition_hz is not None
        else _default_fir_transition(spec, sampling_hz)
    )
    if not (0 < transition < sampling_hz / 2):
        raise ValueError("FIR transition width must be positive and below Nyquist")
    order = max(2, int(np.ceil(3.3 * sampling_hz / transition)))
    if order % 2:
        order += 1
    return order + 1, transition


def design_filter(spec: FilterSpec, sampling_hz: float) -> _DesignedFilter:
    """Design a validated filter without applying it to data."""

    sampling_hz = _validate_sampling(sampling_hz)
    cutoff = _validated_cutoff(spec, sampling_hz)
    if spec.order < 1:
        raise ValueError("Filter order must be at least 1")
    if spec.kind == "notch":
        if spec.family != "butterworth":
            raise ValueError("Notch filtering uses a dedicated second-order IIR design")
        if not np.isfinite(spec.notch_quality) or spec.notch_quality <= 0:
            raise ValueError("Notch quality must be positive and finite")
        b, a = iirnotch(float(cutoff), spec.notch_quality, fs=sampling_hz)
        return _DesignedFilter(spec, sampling_hz, tf2sos(b, a), "sos")
    if spec.family == "butterworth":
        sos = butter(spec.order, cutoff, btype=spec.kind, fs=sampling_hz, output="sos")
        return _DesignedFilter(spec, sampling_hz, sos, "sos")
    if spec.family != "fir":
        raise ValueError(f"Unsupported filter family: {spec.family}")
    if spec.fir_numtaps is None:
        numtaps, transition = _default_fir_numtaps(spec, sampling_hz)
        resolved = replace(spec, fir_numtaps=numtaps, fir_transition_hz=transition)
    else:
        numtaps = spec.fir_numtaps
        resolved = spec
    if numtaps < 3 or numtaps % 2 == 0:
        raise ValueError("Linear-phase FIR filters require an odd number of at least 3 taps")
    taps = firwin(numtaps, cutoff, pass_zero=spec.kind, fs=sampling_hz, window="hamming")
    return _DesignedFilter(resolved, sampling_hz, taps, "fir")


def _segment_ranges(length: int, boundaries: tuple[int, ...] | None) -> tuple[tuple[int, int], ...]:
    if not boundaries:
        return ((0, length),)
    points = tuple(int(point) for point in boundaries)
    if any(point <= 0 or point >= length for point in points):
        raise ValueError("Boundaries must lie strictly inside the signal")
    if tuple(sorted(set(points))) != points:
        raise ValueError("Boundaries must be unique and strictly increasing")
    return tuple(zip((0, *points), (*points, length), strict=True))


def _apply_sos(segment: np.ndarray, sos: np.ndarray, zero_phase: bool) -> np.ndarray:
    if zero_phase:
        try:
            return sosfiltfilt(sos, segment)
        except ValueError as exc:
            raise ValueError(
                "Signal segment is too short for zero-phase IIR filtering; "
                "use a longer segment, lower order, or causal mode"
            ) from exc
    initial = sosfilt_zi(sos) * segment[0]
    return sosfilt(sos, segment, zi=initial)[0]


def _apply_fir(segment: np.ndarray, taps: np.ndarray, zero_phase: bool) -> np.ndarray:
    if zero_phase:
        half = len(taps) // 2
        if segment.size <= half:
            raise ValueError(
                "Signal segment is too short for the requested zero-phase FIR filter"
            )
        padded = np.pad(segment, half, mode="reflect")
        return fftconvolve(padded, taps, mode="valid")
    # A causal FIR starts from rest; its startup transient remains explicit.
    return np.convolve(segment, taps, mode="full")[: segment.size]


def apply_filter(
    values: np.ndarray,
    sampling_hz: float,
    spec: FilterSpec | None = None,
    *,
    boundaries: tuple[int, ...] | None = None,
) -> FilterResult:
    """Apply one reproducible filter independently across optional boundaries.

    ``boundaries`` contains sample indices where a new continuous segment
    starts. No filter state or padding crosses those discontinuities.
    """

    signal = _as_signal(values)
    designed = design_filter(spec or FilterSpec(), sampling_hz)
    ranges = _segment_ranges(signal.size, boundaries)
    output = np.empty_like(signal)
    for start, stop in ranges:
        segment = signal[start:stop]
        if designed.spec.detrend is not None:
            segment = scipy_detrend(segment, type=designed.spec.detrend)
        if designed.form == "sos":
            output[start:stop] = _apply_sos(
                segment, designed.coefficients, designed.spec.zero_phase
            )
        else:
            output[start:stop] = _apply_fir(
                segment, designed.coefficients, designed.spec.zero_phase
            )
    base_order = 2 if designed.spec.kind == "notch" else (
        len(designed.coefficients) - 1
        if designed.form == "fir"
        else designed.spec.order * (2 if designed.spec.kind in ("bandpass", "bandstop") else 1)
    )
    effective_order = base_order * (2 if designed.spec.zero_phase and designed.form == "sos" else 1)
    report = FilterReport(
        spec=designed.spec,
        sampling_hz=designed.sampling_hz,
        implementation=(
            "scipy.signal.sosfiltfilt"
            if designed.form == "sos" and designed.spec.zero_phase
            else "scipy.signal.sosfilt"
            if designed.form == "sos"
            else "centered Hamming-window FIR"
            if designed.spec.zero_phase
            else "causal Hamming-window FIR"
        ),
        coefficient_form=designed.form,
        coefficient_count=int(designed.coefficients.size),
        effective_order=effective_order,
        segments=ranges,
    )
    return FilterResult(output, report)


def frequency_response(
    spec: FilterSpec, sampling_hz: float, *, points: int = 2048
) -> FrequencyResponse:
    """Return the design magnitude response for review and visualization."""

    if points < 16:
        raise ValueError("Frequency response requires at least 16 points")
    designed = design_filter(spec, sampling_hz)
    if designed.form == "sos":
        frequency, response = sosfreqz(designed.coefficients, worN=points, fs=sampling_hz)
    else:
        frequency, response = freqz(designed.coefficients, worN=points, fs=sampling_hz)
    magnitude = 20 * np.log10(np.maximum(np.abs(response), np.finfo(float).tiny))
    if spec.zero_phase and designed.form == "sos":
        magnitude *= 2
    return FrequencyResponse(frequency, magnitude)


def boundaries_from_time(time_s: np.ndarray, *, gap_factor: float = 1.5) -> tuple[int, ...]:
    """Locate large acquisition gaps without treating ordinary jitter as a boundary."""

    time = _as_signal(time_s)
    if gap_factor <= 1:
        raise ValueError("Gap factor must be greater than 1")
    intervals = np.diff(time)
    if (intervals <= 0).any():
        raise ValueError("Time must be strictly increasing")
    threshold = float(np.median(intervals)) * gap_factor
    return tuple(int(index + 1) for index in np.flatnonzero(intervals > threshold))


def lowpass(values: np.ndarray, sampling_hz: float, cutoff_hz: float = 6.0) -> np.ndarray:
    """Backward-compatible exploratory 4th-order zero-phase Butterworth filter."""

    return apply_filter(
        values,
        sampling_hz,
        FilterSpec(kind="lowpass", cutoff_hz=cutoff_hz),
    ).values
