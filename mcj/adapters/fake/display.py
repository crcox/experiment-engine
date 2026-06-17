from typing import Literal, Any, Callable
from mcj.runtime.display_primitives import StimFactory, TextElement, ShapeElement, LineConfig

class FakeText(TextElement):
    def __init__(self, name: str, cfg: dict[str, Any], verbose: bool=False):
        self.name = name
        self.cfg = {}
        self._verbose = verbose
        self.text: str = ""

        if self._verbose:
            print(f"CREATE {self.name}")
            print(f"  WITH cfg={cfg}")

    def set_text(self, text: str):
        self.text = text
        if self._verbose:
            print(f"UPDATE {self.name} text:", text)

    def get_text(self):
        return self.text

    def set_color(self, color: str):
        if self._verbose:
            print(f"UPDATE {self.name} color:", color)

    def draw(self):
        if self._verbose:
            print(f"DRAW {self.name} | text={self.text}")

    def __repr__(self):
        return f"<FakeText name={self.name!r} text={self.text!r}>"


class FakeShape(ShapeElement):
    def __init__(self, name: str, cfg: dict[str, Any], verbose: bool=False):
        self.name = name
        self.cfg = {}
        self._verbose = verbose

        if self._verbose:
            print(f"CREATE {self.name}")
            print(f"  WITH cfg={cfg}")

    def draw(self):
        if self._verbose:
            print(f"DRAW {self.name}")

    def __repr__(self):
        return f"<FakeShape name={self.name!r}>"

class FakeFactory(StimFactory):
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
        self.cfg = {
            "name": name,
            "pos": pos,
            "height": height,
            "color": color,
            "wrapWidth": wrap_width,
            "bold": bold,
            "anchorVert": anchor_vert,
            "anchorHoriz": anchor_horiz,
        }
        return FakeText(name, self.cfg)

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

        cfg = {
            "vertices": shape,
            "pos": pos,
            "size": size, # pyright: ignore
            "lineWidth": line_width, # pyright: ignore
            "lineColor": line_color, # pyright: ignore
            "color": color, # pyright: ignore
            "anchor": anchor_vert+anchor_horiz,
        }
        return FakeShape(name, cfg)


    def flip(self):
        print("FLIP")

    def call_on_flip(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        func(*args, **kwargs)

    def close(self):
        pass

    def version(self) -> None:
        return None


if __name__ == "__main__":
    from mcj.tasks.criterion_judgment.display import CriterionJudgmentPromptDisplay

    display = CriterionJudgmentPromptDisplay(FakeFactory())
    display.update(
        prompt_frame_text="Frame",
        prompt_text="Hello",
        left_text="Left",
        right_text="Right",
    )
    display.draw()

