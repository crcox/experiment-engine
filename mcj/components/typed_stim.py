from __future__ import annotations

from psychopy.visual.window import Window
from psychopy.visual.shape import ShapeStim

class TypedShapeStim(ShapeStim):
    def __init__(
        self,
        *,
        win: Window,
        size: tuple[float, float] | tuple[int, int],
        pos: tuple[float, float] | tuple[int, int],
        lineColor: str | tuple[float, float, float],
        fillColor: str | tuple[float, float, float],
        **kwargs,
    ):
        super().__init__(
            win=win,
            size=size, # pyright: ignore
            pos=pos, # pyright: ignore
            lineColor=lineColor, # pyright: ignore
            fillColor=fillColor, # pyright: ignore
            **kwargs
        )


