from __future__ import annotations

from typing import TypedDict, Literal

Event = dict[str, object]

class BaseEvent(TypedDict):
    type: str
    time: float

class MouseClickEvent(BaseEvent):
    block_index: int
    node_index: int
    button: Literal["left", "middle", "right"]
    x: float
    y: float
    target: str
    target_pos: tuple[float, float]
    target_size: tuple[float, float]
    target_contains_click: bool

class MousePositionEvent(BaseEvent):
    block_index: int
    node_index: int
    button: Literal["left", "middle", "right"]
    sample_reason: Literal["periodic", "button_change"]
    x: float
    y: float

SessionStartEvent = BaseEvent
    
class BlockStartEvent(BaseEvent):
    block_index: int

class BlockAbortEvent(BaseEvent):
    block_index: int
    reason: str

class BlockEndEvent(BaseEvent):
    block_index: int

class TrialStartEvent(BaseEvent):
    block_index: int
    node_index: int
    target: str

class TrialAbortEvent(BaseEvent):
    block_index: int
    node_index: int
    reason: str

class TrialEndEvent(BaseEvent):
    block_index: int
    node_index: int

class EventRecorder:
    """
    Append-only in-memory event stream for a single session.

    Producers emit semantic events.
    Consumers (loggers) read incrementally using cursors.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    def emit(self, event: Event) -> None:
        """
        Record a new event.

        Events must be JSON-serializable dicts.
        """
        self._events.append(event)

    def events(self) -> list[Event]:
        """
        Return the full event list.

        Intended for read-only consumption by loggers.
        """
        return self._events
