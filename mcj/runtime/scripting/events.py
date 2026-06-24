from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class ScriptEvent:
    type: Literal["button", "trigger"]
    code: str | int
    is_press: bool = True
    time: float | None = None
    target: Literal["keyboard", "cedrus"] | None = None

