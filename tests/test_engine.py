import numpy as np
import pandas as pd
import pytest

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.io.csv import validate_frame
from kinoryx.pipeline import analyze_exploratory
from kinoryx.processing.filtering import lowpass


def test_synthetic_reproducible():
    a = generate_demo_dataset()
    b = generate_demo_dataset()
    pd.testing.assert_frame_equal(a, b)


def test_synthetic_metadata():
    info = validate_frame(generate_demo_dataset())
    assert info.rows == 1200
    assert info.available_channels == ("left_gyro_y_deg_s", "right_gyro_y_deg_s")


def test_one_foot_supported():
    frame = generate_demo_dataset().drop(columns="right_gyro_y_deg_s")
    assert validate_frame(frame).available_channels == ("left_gyro_y_deg_s",)


def test_invalid_time_rejected():
    frame = generate_demo_dataset()
    frame.loc[5, "time_s"] = frame.loc[4, "time_s"]
    with pytest.raises(ValueError, match="increasing"):
        validate_frame(frame)


def test_missing_channels_rejected():
    with pytest.raises(ValueError, match="channel"):
        validate_frame(generate_demo_dataset()[["time_s"]])


def test_nan_rejected():
    frame = generate_demo_dataset()
    frame.loc[100, "left_gyro_y_deg_s"] = np.nan
    with pytest.raises(ValueError):
        validate_frame(frame)


def test_filter_preserves_length():
    signal = generate_demo_dataset()["left_gyro_y_deg_s"].to_numpy()
    assert len(lowpass(signal, 100.0)) == len(signal)


def test_invalid_cutoff_rejected():
    with pytest.raises(ValueError, match="Nyquist"):
        lowpass(np.ones(100), 100.0, 50.0)


def test_pipeline_detects_exploratory_candidates():
    result = analyze_exploratory(generate_demo_dataset())
    assert len(result.peaks) > 0
    assert all(p.side in ("left", "right") for p in result.peaks)


def test_raw_not_modified():
    original = generate_demo_dataset()
    copy = original.copy(deep=True)
    analyze_exploratory(original)
    pd.testing.assert_frame_equal(original, copy)
