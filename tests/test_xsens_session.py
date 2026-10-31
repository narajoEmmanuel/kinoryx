"""Tests use synthetic bytes and XML; no private recordings enter GitHub."""

import hashlib
import json
from pathlib import Path

import pytest

from kinoryx.io.xsens_session import verify_research_session


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    files = {
        "sample.mvn": b"synthetic binary motion fixture",
        "sample.mvns": (
            b'<mvns version="2" sessionname="synthetic">'
            b'<file filename="sample.mvn"/>'
            b'<file filename="sample.mvne"/></mvns>'
        ),
        "sample.mvne": (
            b'<mvnext><channels count="1">'
            b'<channel id="0" name="synthetic EMG" frameRate="1000"/>'
            b'</channels><data><sample id="0" value="1.5"/>'
            b'<sample id="0" value="-2.0"/></data></mvnext>'
        ),
    }
    manifest = {
        "schema": "kinoryx.research-session-manifest.v1",
        "dataset_id": "synthetic-test",
        "session_filename": "sample.mvns",
        "files": [],
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
        manifest["files"].append({
            "filename": name,
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path, manifest_path


def test_verify_source_bundle(tmp_path: Path) -> None:
    directory, manifest = _fixture(tmp_path)
    result = verify_research_session(directory, manifest)
    assert result["dataset_id"] == "synthetic-test"
    assert len(result["verified_files"]) == 3
    assert result["source_session_label"] == "synthetic"
    assert result["emg_samples_per_channel"] == 2
    assert result["emg_sampling_hz"] == 1000


def test_detect_tampered_motion_file(tmp_path: Path) -> None:
    directory, manifest = _fixture(tmp_path)
    (directory / "sample.mvn").write_bytes(b"changed binary motion")
    with pytest.raises(ValueError, match="mismatch"):
        verify_research_session(directory, manifest)


def test_detect_bad_session_reference(tmp_path: Path) -> None:
    directory, manifest = _fixture(tmp_path)
    # Update manifest checksum to isolate the session-index integrity check.
    session = directory / "sample.mvns"
    session.write_bytes(session.read_bytes().replace(b"sample.mvne", b"other.mvne"))
    with pytest.raises(ValueError, match="does not reference"):
        verify_research_session(directory, manifest)
