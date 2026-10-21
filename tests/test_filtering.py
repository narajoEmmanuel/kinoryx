import numpy as np
import pytest

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.pipeline import analyze_exploratory
from kinoryx.processing.filtering import (
    FilterSpec,
    apply_filter,
    boundaries_from_time,
    frequency_response,
)


def _magnitude_at(response, frequency_hz: float) -> float:
    index = int(np.argmin(np.abs(response.frequency_hz - frequency_hz)))
    return float(response.magnitude_db[index])


def test_default_response_preserves_gait_band_and_attenuates_noise():
    response = frequency_response(FilterSpec(), 100.0)
    assert _magnitude_at(response, 2.0) > -0.1
    assert _magnitude_at(response, 20.0) < -80


@pytest.mark.parametrize("kind", ["lowpass", "highpass", "bandpass", "bandstop"])
def test_supported_butterworth_responses_preserve_length(kind):
    time = np.arange(1000) / 100.0
    signal = np.sin(2 * np.pi * 2 * time) + np.sin(2 * np.pi * 20 * time)
    cutoff = (3.0, 10.0) if kind.startswith("band") else 6.0
    result = apply_filter(signal, 100.0, FilterSpec(kind=kind, cutoff_hz=cutoff))
    assert result.values.shape == signal.shape
    assert result.report.coefficient_form == "sos"


def test_bandpass_isolates_frequency_inside_band():
    time = np.arange(2000) / 200.0
    low = np.sin(2 * np.pi * 5 * time)
    high = np.sin(2 * np.pi * 40 * time)
    result = apply_filter(
        low + high,
        200.0,
        FilterSpec(kind="bandpass", cutoff_hz=(3.0, 10.0)),
    )
    projection_low = abs(np.vdot(result.values, low))
    projection_high = abs(np.vdot(result.values, high))
    assert projection_low > projection_high * 100


def test_notch_rejects_selected_frequency():
    response = frequency_response(
        FilterSpec(kind="notch", cutoff_hz=50.0, notch_quality=30.0), 200.0
    )
    assert _magnitude_at(response, 50.0) < -40
    assert _magnitude_at(response, 20.0) > -0.1


def test_fir_design_is_odd_length_and_zero_phase():
    time = np.arange(1200) / 100.0
    signal = np.sin(2 * np.pi * 2 * time) + 0.2 * np.sin(2 * np.pi * 20 * time)
    result = apply_filter(
        signal,
        100.0,
        FilterSpec(family="fir", fir_transition_hz=4.0),
    )
    assert result.report.spec.fir_numtaps is not None
    assert result.report.spec.fir_numtaps % 2 == 1
    assert result.report.spec.fir_transition_hz == 4.0
    assert result.report.effective_order == result.report.spec.fir_numtaps - 1
    assert len(result.values) == len(signal)


def test_fir_automatic_design_records_resolved_transition_width():
    signal = np.sin(2 * np.pi * 2 * np.arange(1200) / 100.0)
    result = apply_filter(signal, 100.0, FilterSpec(family="fir"))
    assert result.report.spec.fir_transition_hz == 2.0
    assert result.report.spec.fir_numtaps == 167


def test_causal_mode_is_reported_and_preserves_length():
    signal = np.r_[np.zeros(20), np.ones(180)]
    result = apply_filter(signal, 100.0, FilterSpec(zero_phase=False))
    assert result.report.implementation == "scipy.signal.sosfilt"
    assert len(result.values) == len(signal)


def test_detrending_is_explicit_and_removes_linear_component():
    time = np.arange(1000) / 100.0
    signal = 4 * time + np.sin(2 * np.pi * 2 * time)
    result = apply_filter(
        signal,
        100.0,
        FilterSpec(kind="lowpass", cutoff_hz=6.0, detrend="linear"),
    )
    slope = np.polyfit(time, result.values, 1)[0]
    assert abs(slope) < 0.01


def test_boundaries_are_detected_and_reported_as_independent_segments():
    time = np.r_[np.arange(100) / 100.0, 2.0 + np.arange(100) / 100.0]
    boundaries = boundaries_from_time(time)
    result = apply_filter(np.sin(2 * np.pi * time), 100.0, boundaries=boundaries)
    assert boundaries == (100,)
    assert result.report.segments == ((0, 100), (100, 200))


def test_invalid_designs_fail_before_filtering():
    signal = np.ones(100)
    with pytest.raises(ValueError, match="Nyquist"):
        apply_filter(signal, 100.0, FilterSpec(cutoff_hz=50.0))
    with pytest.raises(ValueError, match="tuple"):
        apply_filter(signal, 100.0, FilterSpec(kind="bandpass", cutoff_hz=5.0))
    with pytest.raises(ValueError, match="odd"):
        apply_filter(
            signal,
            100.0,
            FilterSpec(family="fir", fir_numtaps=20),
        )


def test_pipeline_accepts_a_reproducible_custom_filter():
    spec = FilterSpec(kind="lowpass", cutoff_hz=10.0, order=2)
    result = analyze_exploratory(generate_demo_dataset(), spec)
    assert result.filter_reports
    assert all(report.spec == spec for report in result.filter_reports.values())
