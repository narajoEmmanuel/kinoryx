"""Local reader for MVN external-signal (.mvne) XML recordings.

Preserves scalar samples as provided. No calibration, normalization, muscle
activation inference, synchronization or gait-event detection is performed.
"""

import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

MAX_INPUT_BYTES = 25_000_000


@dataclass(frozen=True)
class EmgChannel:
    id: int
    name: str
    source: str
    source_channel: str
    sampling_hz: float


@dataclass(frozen=True)
class EmgRecording:
    channels: tuple[EmgChannel, ...]
    samples: tuple[tuple[float, ...], ...]
    sample_count: int
    sampling_hz: float
    source_timestamp: str | None

    @property
    def sample_span_s(self) -> float:
        """Elapsed time from first sample to last, not total acquisition duration."""
        return (self.sample_count - 1) / self.sampling_hz


def read_mvne(path: str | Path) -> EmgRecording:
    """Parse a local .mvne XML file, keeping channel values in recording order.

    The header must describe a shared sampling rate. Sample IDs are channel IDs,
    not frame numbers. Timestamp interpretation and absolute sync are unknown.
    """
    source = Path(path)
    if source.suffix.lower() != ".mvne":
        raise ValueError("Expected a .mvne external-signal XML recording")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("MVNE file exceeds the 25 MB local-import safety limit")
    try:
        root = ET.parse(source).getroot()
    except ET.ParseError as exc:
        raise ValueError("Invalid MVNE XML") from exc
    if root.tag != "mvnext":
        raise ValueError("Unexpected root; expected <mvnext>")
    header = root.find("channels")
    data = root.find("data")
    if header is None or data is None:
        raise ValueError("MVNE requires <channels> and <data>")
    channels = []
    for entry in header.findall("channel"):
        try:
            channel = EmgChannel(
                id=int(entry.attrib["id"]),
                name=entry.attrib["name"],
                source=entry.attrib.get("source", ""),
                source_channel=entry.attrib.get("sourceChannel", ""),
                sampling_hz=float(entry.attrib["frameRate"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid channel metadata") from exc
        if not math.isfinite(channel.sampling_hz) or channel.sampling_hz <= 0:
            raise ValueError("Channel sampling rate must be finite and positive")
        channels.append(channel)
    if not channels or len({ch.id for ch in channels}) != len(channels):
        raise ValueError("MVNE channel IDs must be nonempty and unique")
    if len({ch.sampling_hz for ch in channels}) != 1:
        raise ValueError("Mixed channel sampling rates are not supported")
    if header.attrib.get("count") != str(len(channels)):
        raise ValueError("Declared channel count does not match channel metadata")
    values: dict[int, list[float]] = {ch.id: [] for ch in channels}
    for item in data:
        if item.tag != "sample":
            raise ValueError("Unexpected element inside <data>")
        try:
            channel_id = int(item.attrib["id"])
            value = float(item.attrib["value"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid MVNE sample") from exc
        if channel_id not in values or not math.isfinite(value):
            raise ValueError("Unknown channel ID or nonfinite MVNE sample")
        values[channel_id].append(value)
    counts = {len(v) for v in values.values()}
    if len(counts) != 1 or not counts or next(iter(counts)) == 0:
        raise ValueError("Channels must have equal, nonzero sample counts")
    timestamp_node = root.find("mvn")
    timestamp = timestamp_node.get("ts") if timestamp_node is not None else None
    return EmgRecording(
        channels=tuple(channels),
        samples=tuple(tuple(values[ch.id]) for ch in channels),
        sample_count=next(iter(counts)),
        sampling_hz=channels[0].sampling_hz,
        source_timestamp=timestamp,
    )


def export_mvne_csv(source: str | Path, destination: str | Path) -> tuple[Path, Path]:
    """Write source-scale EMG values and channel metadata to local files.

    Use an ignored folder such as data_local/. The values have unspecified units.
    time_s is relative to each channel's first sample, not absolute sync time.
    """
    recording = read_mvne(source)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = target.with_suffix(".metadata.json")
    columns = [f"emg_ch{channel.id}_raw" for channel in recording.channels]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", *columns])
        for index, row in enumerate(zip(*recording.samples)):
            writer.writerow([index / recording.sampling_hz, *row])
    metadata = {
        "source_filename": Path(source).name,
        "source_sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "source_timestamp_uninterpreted": recording.source_timestamp,
        "sampling_hz": recording.sampling_hz,
        "samples_per_channel": recording.sample_count,
        "sample_span_s": recording.sample_span_s,
        "units": "unspecified in MVNE header; raw values preserved",
        "time_reference": "relative to first sample; not externally synchronized",
        "channels": [dict(asdict(ch), csv_column=col) for ch, col in zip(recording.channels, columns)],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return target, metadata_path
