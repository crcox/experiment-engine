from csv import DictWriter
from dataclasses import asdict
from pathlib import Path

from mcj.reporting.criterion_judgment.translator import TrialRecord

def write_trial_records(
    records: list[TrialRecord],
    path: Path,
) -> None:

    if not records:
        return

    with path.open("w", newline="") as f:
        writer = DictWriter(
            f,
            fieldnames=list(asdict(records[0]).keys())
        )

        writer.writeheader()

        for record in records:
            writer.writerow(asdict(record))
