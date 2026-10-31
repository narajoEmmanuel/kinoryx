"""Synthetic integration tests for the disposable research branch."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))
from study_files import study  # noqa: E402


def test_readonly_bundle_summary(tmp_path: Path) -> None:
    data = tmp_path / "data_local"
    data.mkdir()
    (data / "test.mvn").write_bytes(b"synthetic motion placeholder")
    (data / "test.mvns").write_text(
        '<mvns version="2" sessionname="training">'
        '<file filename="test.mvn" timeOffset="0" timeEndOffset="0"/>'
        '<file filename="test.mvne" timeOffset="0" timeEndOffset="0"/>'
        '</mvns>',
        encoding="utf-8",
    )
    (data / "test.mvne").write_text(
        '<mvnext><channels count="2">'
        '<channel id="0" frameRate="1000" name="Synthetic A" source="test"/>'
        '<channel id="1" frameRate="1000" name="Synthetic B" source="test"/>'
        '</channels><data>'
        '<sample id="0" value="1"/><sample id="1" value="-2"/>'
        '<sample id="0" value="3"/><sample id="1" value="4"/>'
        '</data></mvnext>',
        encoding="utf-8",
    )
    result = study(data, data / "study_output", "test.mvns", plots=False)
    assert result["session_index"]["session_name"] == "training"
    assert result["motion_binary"]["decoded"] is False
    assert result["emg"]["sampling_hz"] == 1000
    assert result["emg"]["samples_per_channel"] == 2
    assert len(result["emg"]["channels"]) == 2
    assert (data / "study_output" / "study_summary.json").is_file()
