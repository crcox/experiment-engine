from __future__ import annotations

from psychopy.visual.window import Window
from psychopy.hardware.keyboard import Keyboard
from mcj.components.instructions import InstructionLayout
from mcj.helpers.quit import quit_psychopy
from mcj.instructions.schema import InstructionSlide


def run(win: Window, *,
        layout: InstructionLayout,
        slides: list[InstructionSlide],
        keyboard: Keyboard | None = None
):
    for slide in slides:
        _run_slide(win, layout, slide, keyboard)


def _run_slide(
        win: Window,
        layout: InstructionLayout,
        slide: InstructionSlide,
        keyboard: Keyboard | None = None
) -> None:
    advance = False
    layout.update(slide)

    while not advance:
        layout.draw()
        next_button.draw()
        win.flip()
        mouse_tracker.update()
        last_click = mouse_tracker.last_click(button_filter=["left"])

        if keyboard and keyboard.getKeys(["escape"], waitRelease=False):
            quit_psychopy(win)

        if last_click and next_button.contains(last_click.pos):
            advance = True



