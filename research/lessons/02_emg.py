"""Educational EMG signal inspection, read-only, non-clinical.

Run from the repository root:
    .venv\\Scripts\\python.exe research\\lessons\\02_emg.py
    .venv\\Scripts\\python.exe research\\lessons\\02_emg.py --channel 0 --start 1 --duration .25 --plot

The source values are uncalibrated. Do not interpret RMS as muscular force.
"""
import argparse
from pathlib import Path

import numpy as np

from kinoryx.io.xsens_emg import read_mvne


SOURCE = Path("research/source_data/EMG2_Squats-200714130240.mvne")
OUTPUT_DIR = Path("data_local/study_output")


def inspect_interval(recording, channel_id: int, start_s: float, duration_s: float) -> dict:
    """Describe raw source-scale samples without calibration or filtering."""
    if not np.isfinite(start_s) or start_s < 0:
        raise ValueError("start must be finite and >= 0")
    if not np.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("duration must be finite and > 0")
    available = {channel.id: (channel, samples)
                 for channel, samples in zip(recording.channels, recording.samples)}
    if channel_id not in available:
        raise ValueError(f"Channel {channel_id} is not present")
    channel, samples = available[channel_id]
    rate = recording.sampling_hz
    first = int(np.floor(start_s * rate))
    last = min(recording.sample_count, int(np.ceil((start_s + duration_s) * rate)))
    if first >= recording.sample_count or last <= first:
        raise ValueError("Requested interval is outside the recording")
    raw = np.asarray(samples[first:last], dtype=float)
    return {
        "channel_id": channel.id,
        "channel_name": channel.name,
        "sampling_hz": rate,
        "first_sample_index": first,
        "last_sample_index_exclusive": last,
        "first_sample_time_s": first / rate,
        "last_sample_time_s": (last - 1) / rate,
        "n": raw.size,
        "mean_source_scale": float(np.mean(raw)),
        "min_source_scale": float(np.min(raw)),
        "max_source_scale": float(np.max(raw)),
        "rms_source_scale": float(np.sqrt(np.mean(raw ** 2))),
        "p95_absolute_source_scale": float(np.percentile(np.abs(raw), 95)),
        "raw": raw,
    }


def render_plot(stats: dict, output_dir: Path) -> Path:
    """Save one graph without altering the original recording."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    t = (np.arange(stats["n"]) + stats["first_sample_index"]) / stats["sampling_hz"]
    fig, axis = plt.subplots(figsize=(10, 4))
    axis.plot(t, stats["raw"], linewidth=0.75)
    axis.set(
        title=f"Raw EMG channel {stats['channel_id']}: {stats['channel_name']}",
        xlabel="Relative time (seconds)",
        ylabel="Original source values (units unknown)",
    )
    fig.tight_layout()
    name = (f"lesson02_emg_ch{stats['channel_id']}"
            f"_{stats['first_sample_index']}_{stats['last_sample_index_exclusive']}.png")
    path = output_dir / name
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="KINORYX lesson 02, explore raw EMG")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--channel", type=int, default=None)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float, default=0.25)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"Missing source: {args.source}. Run git pull in the study branch.")
    recording = read_mvne(args.source)
    print(f"File: {args.source.name}")
    print(f"Channels: {len(recording.channels)}, sample rate: {recording.sampling_hz:g} Hz")
    print(f"Samples/channel: {recording.sample_count}, span: {recording.sample_span_s:.3f} s")
    print("WARNING: amplitude units, calibration, and physical sync are UNKNOWN.")
    for channel in recording.channels:
        print(f"  {channel.id}: {channel.name} ({channel.source}, channel {channel.source_channel})")
    if args.channel is None:
        print("Choose --channel 0, 1, 2 or 3 to inspect a time interval.")
        return
    try:
        s = inspect_interval(recording, args.channel, args.start, args.duration)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"\nChannel {s['channel_id']}, {s['channel_name']}")
    print(f"Interval: {s['first_sample_time_s']:.4f} to {s['last_sample_time_s']:.4f} s, "
          f"{s['n']} samples")
    for key in ("mean_source_scale", "min_source_scale", "max_source_scale",
                "rms_source_scale", "p95_absolute_source_scale"):
        print(f"  {key}: {s[key]:.6f}")
    print("All amplitude statistics are in unspecified source scale, not force.")
    if args.plot:
        print("Local graph:", render_plot(s, OUTPUT_DIR))


if __name__ == "__main__":
    main()
