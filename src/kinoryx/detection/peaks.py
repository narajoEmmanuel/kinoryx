"""Exploratory peak candidates; NOT heel strikes or toe-offs."""
from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks


@dataclass(frozen=True)
class PeakCandidate:
    side: str
    time_s: float
    amplitude_deg_s: float
    sample_index: int


def find_candidate_peaks(
    time_s: np.ndarray, angular_velocity: np.ndarray, side: str, sampling_hz: float
) -> list[PeakCandidate]:
    if side not in ("left", "right"):
        raise ValueError("Side must be left or right")
    signal = np.asarray(angular_velocity, dtype=float)
    t = np.asarray(time_s, dtype=float)
    if len(signal) != len(t):
        raise ValueError("Time and signal lengths disagree")
    prominence = max(10.0, 0.3 * float(np.ptp(signal)))
    locations, _ = find_peaks(
        signal, prominence=prominence, distance=max(1, int(0.35 * sampling_hz))
    )
    return [
        PeakCandidate(side, float(t[idx]), float(signal[idx]), int(idx))
        for idx in locations
    ]
