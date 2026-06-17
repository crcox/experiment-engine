from typing import Literal, Callable, Any

from mcj.runtime.display_primitives import TextElement, ShapeElement, StimFactory, LineConfig
from mcj.adapters.psychopy.protocols import WindowLike, TextStimLike, ShapeStimLike

FONT="Arial"

class PsychoPyTextElement(TextElement):
    def __init__(self, stim: TextStimLike):
        self._stim = stim

    def set_text(self, text: str):
        self._stim.text = text

    def get_text(self) -> str:
        return self._stim.text

    def set_color(self, color: str):
        self._stim.color = color

    def draw(self):
        self._stim.draw()


class PsychoPyShapeElement(ShapeElement):
    def __init__(self, stim: ShapeStimLike):
        self._stim = stim

    def draw(self):
        self._stim.draw()


class PsychoPyStimFactory(StimFactory):
    def __init__(self, win: WindowLike):
        from psychopy.visual.text import TextStim
        from psychopy.visual.shape import ShapeStim
        self._win = win
        self._TextStim = TextStim
        self._ShapeStim = ShapeStim

    def create_text(
        self,
        *,
        name: str,
        pos: tuple[float, float],
        height: float,
        color: str,
        wrap_width: float | None = None,
        bold: bool = False,
        anchor_vert: Literal["top", "bottom", "center"] = "center",
        anchor_horiz: Literal["left", "right", "center"] = "center",
    ) -> TextElement:
        stim = self._TextStim(
            win=self._win,
            name=name,
            text="",
            pos=pos,
            height=height,
            color=color,
            wrapWidth=wrap_width,
            bold=bold,
            anchorVert=anchor_vert,
            anchorHoriz=anchor_horiz,
            font=FONT,
        )
        return PsychoPyTextElement(stim)

    def create_known_shape(
        self,
        *,
        name: str,
        shape: Literal["triangle", "rectangle", "circle", "cross", "arrow", "star"]='cross',
        size: tuple[float, float],
        pos: tuple[float, float],
        color: str | None,
        line: LineConfig | None = None,
        anchor_vert: Literal["top", "bottom", "center"] = "center",
        anchor_horiz: Literal["left", "right", "center"] = "center",
    ) -> ShapeElement:
        if line is not None:
            line_width=line.width,
            line_color=line.color
        else:
            line_width=0.0
            line_color=None

        stim = self._ShapeStim(
            win=self._win,
            name=name,
            vertices=shape,
            pos=pos,
            size=size, # pyright: ignore
            lineWidth=line_width, # pyright: ignore
            lineColor=line_color, # pyright: ignore
            color=color, # pyright: ignore
            anchor=anchor_vert+anchor_horiz
        )
        return PsychoPyShapeElement(stim)

    def flip(self):
        self._win.flip()
        

    def call_on_flip(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self._win.callOnFlip(func, *args, **kwargs)

    def close(self):
        self._win.clearAutoDraw()
        self._win.flip()
        self._win.close()

    def version(self):
        from psychopy import __version__ as psychopy_version
        return psychopy_version

