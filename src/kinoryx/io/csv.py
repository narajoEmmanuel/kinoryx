"""Validate the vendor-neutral demonstration CSV contract."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

CHANNELS = ("left_gyro_y_deg_s", "right_gyro_y_deg_s")


@dataclass(frozen=True)
class DatasetInfo:
    rows: int
    sampling_hz: float
    available_channels: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_frame(frame: pd.DataFrame) -> DatasetInfo:
    if "time_s" not in frame:
        raise ValueError("CSV must contain time_s")
    channels = tuple(name for name in CHANNELS if name in frame)
    if not channels:
        raise ValueError("At least one canonical foot gyroscope channel is required")
    if len(frame) < 20:
        raise ValueError("At least 20 samples are needed for exploratory filtering")
    cols = ("time_s", *channels)
    try:
        values = frame.loc[:, cols].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Required columns must contain numeric data") from exc
    if not np.isfinite(values).all():
        raise ValueError("Missing and non-finite samples are not supported")
    dt = np.diff(values[:, 0])
    if (dt <= 0).any():
        raise ValueError("time_s must be strictly increasing")
    median_dt = float(np.median(dt))
    rate = 1.0 / median_dt
    if not (5 <= rate <= 2000):
        raise ValueError("Sampling rate is outside the supported prototype range")
    warnings = []
    if np.max(np.abs(dt - median_dt)) > median_dt * 0.05:
        warnings.append("Irregular sampling detected; resampling is not implemented")
    return DatasetInfo(len(frame), rate, channels, tuple(warnings))


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
