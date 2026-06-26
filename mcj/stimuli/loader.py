from __future__ import annotations

from pathlib import Path

from mcj.runtime.exceptions import DataContractError
from mcj.stimuli.schema import WordMetadata, WordTable
import csv


def load_word_metadata_csv(base_assets_dir: Path) -> WordTable:
    required_fields = ['word', 'domain', 'size', 'danger', 'orthography']
    words = {} 
    path = base_assets_dir / "stimuli.csv"
    with path.open('r') as csvfile:
        word_reader = csv.DictReader(csvfile, fieldnames=required_fields, delimiter=',')
        for row in word_reader:
            missing = set(required_fields) - set(row.keys())
            if missing:
                raise DataContractError()
            if all(k==v for k,v in row.items()):
                # file has header
                continue

            words[row['word']] = WordMetadata(
                word=row['word'],
                domain=row['domain'],
                size=row['size'],
                danger=row['danger'],
                orthography=row['orthography']
            )

    return words

