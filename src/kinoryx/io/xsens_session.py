"""Verify a user-provided local Xsens/Cometa bundle against a public manifest.

The manifest contains filenames and hashes, never private motion recordings.
This does not parse the binary MVN, verify calibration or synchronize systems.
"""

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from kinoryx.io.xsens_emg import read_mvne

SCHEMA = "kinoryx.research-session-manifest.v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_research_session(directory: str | Path, manifest_path: str | Path) -> dict:
    """Verify original file bytes, session references and external EMG structure.

    Raise ValueError on a missing, modified, renamed or invalid file. A successful
    result confirms provenance integrity only, not biomechanical validity.
    """
    root = Path(directory)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("Unsupported research session manifest schema")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != 3:
        raise ValueError("Expected exactly three registered source files")
    names = [entry.get("filename") for entry in entries]
    if len(set(names)) != len(names) or any(
        not isinstance(name, str) or Path(name).name != name or name in ("", ".", "..")
        for name in names
    ):
        raise ValueError("Unsafe or duplicate manifest file names")
    if {Path(name).suffix.lower() for name in names} != {".mvn", ".mvns", ".mvne"}:
        raise ValueError("Manifest must contain one MVN, MVNS and MVNE file")
    session_name = manifest.get("session_filename")
    if session_name not in names or Path(session_name).suffix.lower() != ".mvns":
        raise ValueError("Missing registered MVNS session index")
    session_path = root / session_name
    try:
        xml_root = ET.parse(session_path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError("Unable to read MVNS session XML") from exc
    if xml_root.tag != "mvns":
        raise ValueError("Unexpected MVNS root element")
    referenced = [element.get("filename") for element in xml_root.findall("file")]
    expected_references = sorted(name for name in names if name != session_name)
    if sorted(referenced) != expected_references:
        raise ValueError("Session XML does not reference the expected files")
    verified = []
    for entry in entries:
        path = root / entry["filename"]
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or unsafe research file: {entry['filename']}")
        if path.stat().st_size != entry.get("size_bytes"):
            raise ValueError(f"Size mismatch: {entry['filename']}")
        if _sha256(path) != entry.get("sha256"):
            raise ValueError(f"SHA-256 mismatch: {entry['filename']}")
        verified.append(entry["filename"])
    emg_path = next(root / name for name in names if name.lower().endswith(".mvne"))
    emg = read_mvne(emg_path)
    return {
        "dataset_id": manifest["dataset_id"],
        "verified_files": verified,
        "source_session_label": xml_root.get("sessionname"),
        "emg_channel_count": len(emg.channels),
        "emg_samples_per_channel": emg.sample_count,
        "emg_sampling_hz": emg.sampling_hz,
        "limitations": "File integrity only; no validated biomechanics or synchronization",
    }
