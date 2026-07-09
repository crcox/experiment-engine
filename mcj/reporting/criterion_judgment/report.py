from pathlib import Path
from typing import Sequence

from mcj.reporting.criterion_judgment.translator import translate
from mcj.reporting.csv import write_trial_records
from mcj.runtime.events import EventDict


def build_trial_csv(
    events: Sequence[EventDict],
    output_path: Path,
) -> None:

    records = translate(events)
    write_trial_records(records, output_path)
