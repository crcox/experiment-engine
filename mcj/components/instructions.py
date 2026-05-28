from __future__ import annotations

from psychopy.visual.window import Window
from psychopy.visual.text import TextStim
from mcj.instructions.schema import InstructionSlide

class InstructionLayout:
    def __init__(self, win: Window):
        self.win = win

        title_text_height = 0.06
        body_text_height = 0.045
        title_box_top = 0.44
        title_box_bottom = title_box_top - title_text_height
        vspace = 0.05
        body_box_top = title_box_bottom - vspace

        self.title_stim: TextStim = TextStim(
            win,
            pos=(0, title_box_top),
            anchorVert="top",
            height=title_text_height,
            bold=True
        )
        self.body_stim: TextStim = TextStim(
            self.win,
            pos=(0, body_box_top),
            anchorVert="top",
            height=body_text_height,
            wrapWidth=1.4
        )


    def update(self, slide: InstructionSlide):
        self.title_stim.text = slide.get("title", "")
        self.body_stim.text = slide.get("body", "")


    def draw(self):
        self.title_stim.draw()
        self.body_stim.draw()
