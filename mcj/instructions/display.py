from __future__ import annotations

from mcj.runtime.display_primitives import StimFactory
from mcj.instructions.schema import InstructionSlide

class InstructionDisplay:
    def __init__(self, factory: StimFactory):
        self.factory = factory

        title_text_height = 0.06
        body_text_height = 0.045
        title_box_top = 0.44
        title_box_bottom = title_box_top - title_text_height
        vspace = 0.05
        body_box_top = title_box_bottom - vspace

        self.title_stim = factory.create_text(
            name="instruction_title",
            pos=(0, title_box_top),
            height=title_text_height,
            color="white",
            anchor_vert="top",
            bold=True,
        )
        self.body_stim = factory.create_text(
            name="instruction_body",
            pos=(0, body_box_top),
            height=body_text_height,
            color="white",
            anchor_vert="top",
            wrap_width=0.7,
        )


    def update(self, slide: InstructionSlide):
        self.title_stim.set_text(slide.title)
        self.body_stim.set_text(slide.body)


    def draw(self):
        self.title_stim.draw()
        self.body_stim.draw()
