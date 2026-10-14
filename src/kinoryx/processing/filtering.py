"""Zero-phase Butterworth low-pass filtering for exploratory demonstration."""
import numpy as np
from scipy.signal import butter, sosfiltfilt


def lowpass(values: np.ndarray, sampling_hz: float, cutoff_hz: float = 6.0) -> np.ndarray:
    signal = np.asarray(values, dtype=float)
    if signal.ndim != 1 or len(signal) < 20:
        raise ValueError("Expected a one-dimensional signal with at least 20 samples")
    if not np.isfinite(signal).all():
        raise ValueError("Signal contains non-finite values")
    if not (0 < cutoff_hz < sampling_hz / 2):
        raise ValueError("Cutoff must lie below the Nyquist frequency")
    sos = butter(4, cutoff_hz, btype="lowpass", fs=sampling_hz, output="sos")
    return sosfiltfilt(sos, signal)
