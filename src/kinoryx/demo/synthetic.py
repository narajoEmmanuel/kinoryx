"""Reproducible IMU-like demonstration signals, not human measurements."""
import numpy as np
import pandas as pd


def generate_demo_dataset(duration_s: float = 12.0, sampling_hz: float = 100.0) -> pd.DataFrame:
    if duration_s < 1.0 or not (20 <= sampling_hz <= 1000):
        raise ValueError("Invalid synthetic dataset parameters")
    rng = np.random.default_rng(43)
    time = np.arange(0.0, duration_s, 1.0 / sampling_hz)
    angular_frequency = 2 * np.pi * 0.95
    left = 75 * np.sin(angular_frequency * time) + 9 * np.sin(2 * angular_frequency * time)
    right = 71 * np.sin(angular_frequency * time + np.pi) + 8 * np.sin(
        2 * angular_frequency * time + 0.25
    )
    return pd.DataFrame(
        {
            "time_s": time,
            "left_gyro_y_deg_s": left + rng.normal(0, 2.5, len(time)),
            "right_gyro_y_deg_s": right + rng.normal(0, 2.5, len(time)),
        }
    )
