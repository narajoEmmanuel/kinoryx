"""Protect exactly preserved three-source study dataset on GitHub."""

import hashlib
from pathlib import Path
import sys

from kinoryx.io.xsens_emg import read_mvne

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "source_data"
sys.path.insert(0, str(ROOT / "research"))
from study_files import study  # noqa: E402


def test_original_three_sources_have_expected_hashes() -> None:
    expected = {
        "EMG2_Squats.mvn": "2881fe6feb8c274bbfcbd50b92ca44d29f8469dad5cb9294af1716b87620692d",
        "EMG2_Squats.mvns": "3e0550c05c372a17a94582d9117f34c94bcce04d39e582febbbc5e6101bbf463",
        "EMG2_Squats-200714130240.mvne": (
            "17bf9261d73db6b3d94b36b5f334555c3cad6e87ecbce17f422cd62891b9101f"
        ),
    }
    for filename, sha256 in expected.items():
        assert hashlib.sha256((DATA / filename).read_bytes()).hexdigest() == sha256


def test_emg_headers_are_present() -> None:
    emg = read_mvne(DATA / "EMG2_Squats-200714130240.mvne")
    assert len(emg.channels) == 4
    assert emg.sampling_hz == 2000
    assert emg.sample_count == 16527


def test_complete_source_inventory_without_claiming_motion_decode(tmp_path: Path) -> None:
    report = study(DATA, tmp_path / "study_output", "EMG2_Squats.mvns", plots=False)
    assert report["session_index"]["session_name"] == "EMG2_Walkig"
    assert report["emg"]["samples_per_channel"] == 16527
    assert report["motion_binary"]["decoded"] is False
    assert report["motion_binary"]["file"]["sha256"] == "2881fe6feb8c274bbfcbd50b92ca44d29f8469dad5cb9294af1716b87620692d"
    assert all(item["exists"] for item in report["session_index"]["references"])
    assert (tmp_path / "study_output" / "study_summary.json").exists()
