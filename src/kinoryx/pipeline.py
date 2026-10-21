"""Headless data processing. No UI dependency."""
from dataclasses import dataclass

import pandas as pd

from kinoryx.detection.peaks import PeakCandidate, find_candidate_peaks
from kinoryx.io.csv import DatasetInfo, validate_frame
from kinoryx.processing.filtering import (
    FilterReport,
    FilterSpec,
    apply_filter,
    boundaries_from_time,
)


@dataclass
class ExploratoryResult:
    raw: pd.DataFrame
    filtered: pd.DataFrame
    info: DatasetInfo
    peaks: list[PeakCandidate]
    filter_reports: dict[str, FilterReport]


def analyze_exploratory(
    frame: pd.DataFrame, filter_spec: FilterSpec | None = None
) -> ExploratoryResult:
    info = validate_frame(frame)
    raw = frame.loc[:, ["time_s", *info.available_channels]].copy()
    filtered = raw.copy()
    candidates = []
    reports = {}
    boundaries = boundaries_from_time(raw["time_s"].to_numpy())
    for channel in info.available_channels:
        result = apply_filter(
            raw[channel].to_numpy(),
            info.sampling_hz,
            filter_spec,
            boundaries=boundaries,
        )
        filtered[channel] = result.values
        reports[channel] = result.report
        side = channel.split("_", 1)[0]
        candidates.extend(
            find_candidate_peaks(
                raw["time_s"].to_numpy(), filtered[channel].to_numpy(), side, info.sampling_hz
            )
        )
    return ExploratoryResult(
        raw,
        filtered,
        info,
        sorted(candidates, key=lambda p: p.time_s),
        reports,
    )
