from __future__ import annotations

from psychopy.visual.text import TextStim
from psychopy.visual.window import Window
from typing import Sequence
from numpy import linspace

class QuestionText:
    def __init__(self, win: Window):
        self._stim = TextStim(
            win=win,
            name="question_text",
            text="",
            font="Arial",
            pos=(0.0, 0.3),
            height=0.05,
            color=(-1.0, -1.0, -1.0),
            colorSpace="rgb",
            languageStyle="LTR",
        )

    def set(self, question: str) -> None:
        self._stim.text = question

    def draw(self) -> None:
        self._stim.draw()


class OptionsText:
    def __init__(
            self,
            win: Window,
            options: Sequence[str],
            limits: tuple[float, float]
        ):
        self._options: list[tuple[str, TextStim]] = []
        self._selected: int | None = None

        positions = [float(p) for p
                     in linspace(limits[0], limits[1], len(options))]

        for i, (label, x) in enumerate(zip(options, positions)):
            stim = TextStim(
                win=win,
                name=f"opt_{i:d}",
                text=label,
                font='Arial',
                pos=(x, 0.0),
                height=0.05,
                wrapWidth=None,
                color=(-1.0,-1.0,-1.0),
                colorSpace='rgb',
                languageStyle='LTR'
            )
            self._options.append((label, stim))

    def draw(self) -> None:
        for _,stim in self._options:
            stim.draw()

    def highlight(self, idx: int) -> None:
        for i, (_, stim) in enumerate(self._options):
            stim.color = (1, -1, -1) if i == idx else (-1, -1, -1)

    def handle_click(self, pos: tuple[float, float]) -> int | None:
        for i, (_, stim) in enumerate(self._options):
            if stim.contains(pos):
                self._selected = i
                self.highlight(i)
                return i
        return None
