"""Headless data processing. No UI dependency."""
from dataclasses import dataclass

import pandas as pd

from kinoryx.detection.peaks import PeakCandidate, find_candidate_peaks
from kinoryx.io.csv import DatasetInfo, validate_frame
from kinoryx.processing.filtering import lowpass


@dataclass
class ExploratoryResult:
    raw: pd.DataFrame
    filtered: pd.DataFrame
    info: DatasetInfo
    peaks: list[PeakCandidate]


def analyze_exploratory(frame: pd.DataFrame) -> ExploratoryResult:
    info = validate_frame(frame)
    raw = frame.loc[:, ["time_s", *info.available_channels]].copy()
    filtered = raw.copy()
    candidates = []
    for channel in info.available_channels:
        filtered[channel] = lowpass(raw[channel].to_numpy(), info.sampling_hz)
        side = channel.split("_", 1)[0]
        candidates.extend(
            find_candidate_peaks(
                raw["time_s"].to_numpy(), filtered[channel].to_numpy(), side, info.sampling_hz
            )
        )
    return ExploratoryResult(raw, filtered, info, sorted(candidates, key=lambda p: p.time_s))
