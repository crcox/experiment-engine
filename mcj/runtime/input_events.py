from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum

class ButtonDevice(str, Enum):
    KEYBOARD="keyboard"
    CEDRUS="Cedrus Lumina"
    SCRIPT="script"

@dataclass(frozen=True)
class TriggerEvent:
    time: float
    device: ButtonDevice
    is_press: bool
    device_time_ms: int
    system_time_s: float

@dataclass(frozen=True)
class ButtonEvent:
    time: float
    code: str
    device: ButtonDevice
    is_press: bool
    device_time_ms: int | None=None
    system_time_s: float | None=None

@dataclass(frozen=True)
class MouseClick:
    block_index: int
    node_index: int
    button: Literal["left", "middle", "right"]
    x: float
    y: float
    target: str
    target_pos: tuple[float, float]
    target_size: tuple[float, float]
    target_contains_click: bool

@dataclass(frozen=True)
class MousePosition:
    block_index: int
    node_index: int
    button: Literal["left", "middle", "right"]
    sample_reason: Literal["periodic", "button_change"]
    x: float
    y: float


DiscreteInputEvent = Union[
    TriggerEvent,
    ButtonEvent,
    MouseClick,
]

ContinuousInputEvent = Union[
    MousePosition,
]

InputEvent = Union[DiscreteInputEvent, ContinuousInputEvent]

