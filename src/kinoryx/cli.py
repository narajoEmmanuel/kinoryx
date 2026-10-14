"""Small command line entrypoint for local research experiments."""
import argparse
from pathlib import Path

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.io.csv import read_csv, validate_frame
from kinoryx.pipeline import analyze_exploratory


def main() -> None:
    parser = argparse.ArgumentParser(description="KINORYX, exploratory gait data tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Write an explicitly synthetic CSV")
    for action in ("inspect", "explore"):
        sub.add_parser(action).add_argument("csv")
    args = parser.parse_args()
    if args.command == "demo":
        target = Path("data_local/demo_synthetic.csv")
        target.parent.mkdir(parents=True, exist_ok=True)
        generate_demo_dataset().to_csv(target, index=False)
        print(f"Saved SYNTHETIC demonstration to {target}")
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
