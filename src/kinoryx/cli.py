"""Small command line entrypoint for local research experiments."""
import argparse
from pathlib import Path

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.io.csv import read_csv, validate_frame
from kinoryx.io.xsens_emg import export_mvne_csv, read_mvne
from kinoryx.io.xsens_session import verify_research_session
from kinoryx.pipeline import analyze_exploratory


def main() -> None:
    parser = argparse.ArgumentParser(description="KINORYX, exploratory gait data tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Write an explicitly synthetic CSV")
    for action in ("inspect", "explore"):
        sub.add_parser(action).add_argument("csv")
    sub.add_parser("inspect-emg", help="Inspect local MVNE EMG channel metadata").add_argument("mvne")
    emg_export = sub.add_parser("export-emg", help="Export local MVNE EMG values without scaling")
    emg_export.add_argument("mvne")
    emg_export.add_argument("--output", help="CSV destination (default: ignored data_local/)")
    session_check = sub.add_parser("verify-session", help="Verify approved MVN/Cometa source bundle")
    session_check.add_argument("directory", nargs="?", default="data_local")
    session_check.add_argument(
        "--manifest", default="examples/research/EMG2_Squats.manifest.json"
    )
    args = parser.parse_args()
    if args.command == "demo":
        target = Path("data_local/demo_synthetic.csv")
        target.parent.mkdir(parents=True, exist_ok=True)
        generate_demo_dataset().to_csv(target, index=False)
        print(f"Saved SYNTHETIC demonstration to {target}")
        return
    if args.command == "verify-session":
        result = verify_research_session(args.directory, args.manifest)
        print(f"Verified dataset: {result['dataset_id']}")
        for name in result["verified_files"]:
            print(f"  SHA-256 / size OK: {name}")
        print(
            f"EMG: {result['emg_channel_count']} channels, "
            f"{result['emg_samples_per_channel']} samples/channel, "
            f"{result['emg_sampling_hz']:g} Hz"
        )
        print(result["limitations"])
        return
    if args.command in ("inspect-emg", "export-emg"):
        info = read_mvne(args.mvne)
        print(f"{info.sample_count} samples/channel; {info.sampling_hz:g} Hz; {info.sample_span_s:.3f} s span")
        for channel in info.channels:
            print(f"  ch{channel.id}: {channel.name} ({channel.source} {channel.source_channel})")
        print("UNVALIDATED RAW EMG. Units and absolute sync unknown; not gait events.")
        if args.command == "export-emg":
            output = args.output or str(Path("data_local") / f"{Path(args.mvne).stem}_emg.csv")
            csv_path, metadata_path = export_mvne_csv(args.mvne, output)
            print(f"Local export: {csv_path} | metadata: {metadata_path}")
        return
    frame = read_csv(args.csv)
    info = validate_frame(frame)
    print(f"{info.rows} rows, {info.sampling_hz:.2f} Hz, channels: {info.available_channels}")
    for warning in info.warnings:
        print("Warning:", warning)
    if args.command == "explore":
        result = analyze_exploratory(frame)
        print(f"{len(result.peaks)} UNVALIDATED peak candidates; not gait events.")


if __name__ == "__main__":
    main()
