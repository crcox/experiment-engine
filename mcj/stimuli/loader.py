from __future__ import annotations

from psychopy.visual.window import Window
from psychopy.visual.text import TextStim
from mcj.config.paths import paths
from mcj.stimuli.schema import StimulusPool
from mcj.runtime.exceptions import DataContractError
from mcj.stimuli.schema import Word
import csv


def _read_words() -> list[Word]:
    required_fields = ['word', 'domain', 'size', 'danger', 'orthography']
    words = []
    with paths.WORDS_CSV.open('r') as csvfile:
        word_reader = csv.DictReader(csvfile, fieldnames=required_fields, delimiter=',')
        for row in word_reader:
            missing = set(required_fields) - set(row.keys())
            if missing:
                raise DataContractError()

            words.append(Word(
                word=row['word'],
                domain=row['domain'],
                size=row['size'],
                danger=row['danger'],
                orthography=row['orthography'],
                stimulus=None
            ))

    return words


def load_stimulus_pool(win: Window) -> StimulusPool:
    """
    Load all stimuli and create TextStim objects once and return them
    structured by role.
    """

    words: list[Word] = _read_words()
    stimulus_pool: dict[Word, TextStim] = {}
    for word in words:
        stimulus_pool[word] = word.build_stimulus(win)

    return stimulus_pool 

