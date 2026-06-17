from dataclasses import dataclass

@dataclass(frozen=True)
class KeyPress:
    name: str
    rt: float
    tDown: bool
    duration: float | None


