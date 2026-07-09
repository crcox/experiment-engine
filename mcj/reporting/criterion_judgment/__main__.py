from pathlib import Path
import json
import sys

from mcj.reporting.criterion_judgment.report import build_trial_csv

def load_events(path: Path) -> list:
    with path.open("r") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]

def generate_report(session_log_path: Path) -> Path:

    trial_record_path = (
        session_log_path.parent
        / f"{session_log_path.stem}_trials.csv"
    )

    events = load_events(session_log_path)

    build_trial_csv(events, trial_record_path)

    return trial_record_path

def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: python -m mcj.reporting.criterion_judgment session.json"
        )

    session_log_path = Path(sys.argv[1])

    if not session_log_path.exists():
        raise SystemExit(
            f"file does not exist: {session_log_path}"
        )

    generate_report(session_log_path)

if __name__ == "__main__":
    main()
