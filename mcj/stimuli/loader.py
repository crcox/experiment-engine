from __future__ import annotations

from psychopy.visual.window import Window
from psychopy.visual.text import TextStim
from mcj.config.paths import paths
from mcj.runtime.exceptions import DataContractError
from mcj.stimuli.schema import WordMetadata, WordTable, StimulusPool
import csv


def load_word_metadata_csv() -> WordTable:
    required_fields = ['word', 'domain', 'size', 'danger', 'orthography']
    words = {} 
    with paths.WORDS_CSV.open('r') as csvfile:
        word_reader = csv.DictReader(csvfile, fieldnames=required_fields, delimiter=',')
        for row in word_reader:
            missing = set(required_fields) - set(row.keys())
            if missing:
                raise DataContractError()

            words[row['word']] = WordMetadata(
                word=row['word'],
                domain=row['domain'],
                size=row['size'],
                danger=row['danger'],
                orthography=row['orthography'],
                stimulus=None
            )

    return words


def build_stimulus_pool(win: Window, word_table: WordTable) -> StimulusPool:
    """
    Load all stimuli and create TextStim objects once and return them
    as a reusable pool.
    """
    def build_stimulus(word: str) -> TextStim:
        return TextStim(
            win=win,
            text=word,
            name=f"word_{word}",
            color=[1.0, 1.0, 1.0],
            colorSpace="rgb"
        )

    return {w: build_stimulus(w) for w in word_table.keys()}

