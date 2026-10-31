"""Read-only exploratory inspection of the supplied MVNS, MVN and MVNE sources.

Writes metadata and descriptive EMG plots only beneath an ignored local folder.
Does NOT decode motion frames, validate activation or link data to Qualisys.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from kinoryx.io.xsens_emg import read_mvne


def fingerprint(path: Path) -> dict:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return {"name": path.name, "size_bytes": path.stat().st_size, "sha256": sha.hexdigest()}


def read_session(path: Path) -> dict:
    root = ET.parse(path).getroot()
    if root.tag != "mvns":
        raise ValueError("Expected MVNS XML session")
    refs = []
    for element in root.findall("file"):
        name = element.get("filename", "")
        if name in ("", ".", "..") or Path(name).name != name:
            raise ValueError("Unsafe MVNS file reference")
        refs.append({
            "filename": name,
            "exists": (path.parent / name).is_file(),
            "start_offset_as_written": element.get("timeOffset"),
            "end_offset_as_written": element.get("timeEndOffset"),
        })
    return {
        "file": fingerprint(path),
        "session_name": root.get("sessionname"),
        "comment": root.findtext("comment"),
        "references": refs,
        "caution": "Offsets alone do not prove signal-level synchronization",
    }


def read_motion_fingerprint(path: Path) -> dict:
    with path.open("rb") as stream:
        prefix = stream.read(32)
    return {
        "file": fingerprint(path),
        "first_32_bytes_hex": prefix.hex(),
        "decoded": False,
        "caution": "Binary MVN structure not decoded. No joint metrics inferred",
    }


def read_emg(path: Path, window_seconds: float = 0.25) -> tuple[dict, dict]:
    recording = read_mvne(path)
    window_size = max(1, round(window_seconds * recording.sampling_hz))
    channels, chart_data = [], {}
    for channel, samples in zip(recording.channels, recording.samples):
        x = np.asarray(samples, dtype=float)
        windows = [
            {
                "start_time_s": start / recording.sampling_hz,
                "sample_count": min(window_size, len(x) - start),
                "rms_source_scale": float(
                    np.sqrt(np.mean(x[start:start + window_size] ** 2))
                ),
            }
            for start in range(0, len(x), window_size)
        ]
        channels.append({
            "id": channel.id,
            "name_from_header": channel.name,
            "source": channel.source,
            "source_channel": channel.source_channel,
            "mean_source_scale": float(np.mean(x)),
            "standard_deviation_source_scale": float(np.std(x)),
            "min_source_scale": float(np.min(x)),
            "max_source_scale": float(np.max(x)),
            "rms_source_scale": float(np.sqrt(np.mean(x ** 2))),
            "p95_abs_source_scale": float(np.percentile(np.abs(x), 95)),
            "rms_windows": windows,
        })
        chart_data[channel.id] = (channel.name, x, windows)
    return {
        "file": fingerprint(path),
        "sampling_hz": recording.sampling_hz,
        "samples_per_channel": recording.sample_count,
        "sample_span_s": recording.sample_span_s,
        "timestamp_uninterpreted": recording.source_timestamp,
        "units": "Unknown. Source-scale values only",
        "channels": channels,
    }, chart_data


def derived_files(data_dir: Path) -> dict:
    results = {}
    for filename in ("EMG2_Squats_emg.csv", "EMG2_Squats_emg.metadata.json"):
        path = data_dir / filename
        if not path.is_file():
            continue
        info = {"file": fingerprint(path)}
        if path.suffix == ".csv":
            with path.open(encoding="utf-8", newline="") as stream:
                rows = csv.reader(stream)
                info["columns"] = next(rows, [])
                info["row_count"] = sum(1 for _ in rows)
        else:
            info["metadata_keys"] = sorted(json.loads(path.read_text(encoding="utf-8")))
        results[filename] = info
    return results


def plot_emg(chart_data: dict, sampling_hz: float, output_dir: Path) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_names = []
    for channel_id, (name, signal, windows) in chart_data.items():
        for view in ("raw", "rms"):
            fig, axis = plt.subplots(figsize=(11, 3.5))
            if view == "raw":
                axis.plot(np.arange(signal.size) / sampling_hz, signal, lw=0.65)
                axis.set_ylabel("Amplitude as recorded (units unknown)")
            else:
                axis.plot(
                    [item["start_time_s"] for item in windows],
                    [item["rms_source_scale"] for item in windows],
                    marker="o",
                )
                axis.set_ylabel("Window RMS (source scale)")
            axis.set_xlabel("Relative time (seconds)")
            axis.set_title(f"EMG channel {channel_id}, {name}, {view}")
            fig.tight_layout()
            target = output_dir / f"emg_ch{channel_id}_{view}.png"
            fig.savefig(target, dpi=140)
            plt.close(fig)
            output_names.append(target.name)
    return output_names


def study(data_dir: Path, output_dir: Path, session_file: str, plots: bool) -> dict:
    session = read_session(data_dir / session_file)
    mvn = [entry["filename"] for entry in session["references"]
           if entry["filename"].lower().endswith(".mvn")]
    mvne = [entry["filename"] for entry in session["references"]
            if entry["filename"].lower().endswith(".mvne")]
    if len(mvn) != 1 or len(mvne) != 1:
        raise ValueError("Expected exactly one MVN and MVNE source")
    emg_path = data_dir / mvne[0]
    if not emg_path.is_file():
        raise FileNotFoundError(f"Missing EMG file: {emg_path}")
    emg_summary, chart_data = read_emg(emg_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "session_index": session,
        "motion_binary": (
            read_motion_fingerprint(data_dir / mvn[0])
            if (data_dir / mvn[0]).is_file()
            else {
                "filename": mvn[0],
                "available": False,
                "decoded": False,
                "caution": "Binary MVN not present in GitHub; only its manifest hash is recorded",
            }
        ),
        "emg": emg_summary,
        "derived": derived_files(data_dir),
        "qualisys_reference": "https://report.qualisys.com/r/f8pMFlrTA/details",
        "cross_system_sync": "UNVERIFIED",
        "research_limit": "Only source metadata and descriptive EMG statistics",
    }
    if plots:
        summary["plots"] = plot_emg(chart_data, emg_summary["sampling_hz"], output_dir)
    (output_dir / "study_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="KINORYX study-only file inspection")
    parser.add_argument("--data-dir", type=Path, default=Path("research/source_data"))
    parser.add_argument("--output-dir", type=Path, default=Path("data_local/study_output"))
    parser.add_argument("--session", default="EMG2_Squats.mvns")
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()
    result = study(args.data_dir, args.output_dir, args.session, args.plots)
    emg = result["emg"]
    print(f"Session name in file: {result['session_index']['session_name']}")
    print(f"EMG: {len(emg['channels'])} channels at {emg['sampling_hz']:g} Hz, "
          f"{emg['samples_per_channel']} samples each")
    print(f"Study outputs: {args.output_dir}")
    print("The MVN is not decoded; Qualisys synchronization and EMG units are unverified.")


if __name__ == "__main__":
    main()
