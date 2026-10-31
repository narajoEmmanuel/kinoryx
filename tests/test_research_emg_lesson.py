"""Only synthetic samples, independent from the real recording."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pytest

from kinoryx.io.xsens_emg import EmgChannel, EmgRecording


def _lesson():
    source = Path(__file__).resolve().parents[1] / "research" / "lessons" / "02_emg.py"
    spec = spec_from_file_location("kinoryx_lesson_02_emg", source)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _recording() -> EmgRecording:
    return EmgRecording(
        channels=(EmgChannel(0, "Synthetic", "Synthetic", "1", 2.0),),
        samples=((1.0, -1.0, 2.0, -2.0),),
        sample_count=4,
        sampling_hz=2.0,
        source_timestamp=None,
    )


def test_interval_respects_relative_time_and_rms() -> None:
    result = _lesson().inspect_interval(_recording(), 0, 0.0, 1.0)
    assert result["n"] == 2
    assert result["first_sample_time_s"] == 0.0
    assert result["last_sample_time_s"] == 0.5
    assert result["mean_source_scale"] == 0.0
    assert result["rms_source_scale"] == pytest.approx(1.0)
    np.testing.assert_array_equal(result["raw"], [1.0, -1.0])


def test_interval_can_clip_at_last_sample() -> None:
    result = _lesson().inspect_interval(_recording(), 0, 1.5, 1.0)
    assert result["n"] == 1
    assert result["first_sample_index"] == 3
    assert result["last_sample_time_s"] == 1.5


@pytest.mark.parametrize("channel,start,duration", [
    (3, 0, 1),
    (0, -1, 1),
    (0, 0, 0),
    (0, 10, 1),
    (0, float("nan"), 1),
])
def test_invalid_requests_are_rejected(channel: int, start: float, duration: float) -> None:
    with pytest.raises(ValueError):
        _lesson().inspect_interval(_recording(), channel, start, duration)
