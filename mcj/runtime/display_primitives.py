from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Callable, Any

class TextElement(ABC):
    @abstractmethod
    def set_text(self, text: str) -> None: ...

    @abstractmethod
    def get_text(self) -> str: ...

    @abstractmethod
    def set_color(self, color: str) -> None: ...

    @abstractmethod
    def draw(self) -> None: ...

class ShapeElement(ABC):
    @abstractmethod
    def draw(self) -> None: ...

@dataclass(frozen=True)
class LineConfig:
    width: float
    color: str

class StimFactory(ABC):

    @abstractmethod
    def create_text(
        self,
        *,
        name: str,
        pos: tuple[float, float],
        height: float,
        color: str,
        wrap_width: float | None = None,
        bold: bool = False,
        anchor_vert: Literal["top", "bottom", "center"]="center",
        anchor_horiz: Literal["left", "right", "center"]="center",
    ) -> TextElement:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def flip(self) -> None: ...

    @abstractmethod
    def call_on_flip(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def version(self) -> str | None: ...
