from collections.abc import Callable
from typing import Any, Protocol

from psychopy.hardware.keyboard import KeyPress


class WindowLike(Protocol):
    def flip(self) -> None: ...
    def close(self) -> None: ...
    def callOnFlip(
        self, function: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None: ...
    def clearAutoDraw(self) -> None: ...


class TextStimLike(Protocol):
    name: Any
    text: Any
    color: Any

    def draw(self) -> None: ...


class ShapeStimLike(Protocol):
    name: Any
    vertices: Any
    fillColor: Any
    lineColor: Any
    lineWidth: Any

    def draw(self) -> None: ...


class KeyboardLike(Protocol):
    def getKeys(
        self,
        keyList: list[Any] | None = None,
        ignoreKeys: list[Any] | None = None,
        waitRelease: bool = True,
        clear: bool = True,
    ) -> list[KeyPress]: ...

    def clearEvents(self, eventType: Any = None) -> None: ...
