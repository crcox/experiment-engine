from __future__ import annotations

from typing import Callable, Sequence, Literal
from dataclasses import dataclass
from collections import deque

from mcj.runtime.time import Clock
from mcj.runtime.input import InputAdapter, AdapterType
from mcj.runtime.input_events import ButtonEvent, TriggerEvent, ButtonDevice

@dataclass(frozen=True)
class ScriptEvent:
    type: Literal["button", "trigger"]
    code: str | int
    is_press: bool = True

class ScriptedInputAdapter(InputAdapter):
    _clock: Clock
    _script: deque[ScriptEvent] 
    _event_buffer: list[ButtonEvent | TriggerEvent]

    def __init__(
        self,
        clock: Clock,
        script: Sequence[ScriptEvent]
    ):
        self._clock = clock
        self._script = deque(script)
        self._event_buffer = []

    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.SCRIPTED

    def update(self) -> None:
        raw = self._script.popleft()
        self._event_buffer.append(_materialize(raw, self._clock))

    def pop_events(self) -> list[ButtonEvent | TriggerEvent]:
        events = self._event_buffer
        self._event_buffer = []
        return events

    def peek_events(self) -> list[ButtonEvent | TriggerEvent]:
        """
        Return staged events without clearing them.
        """
        events = list(self._event_buffer)
        return events

    def clear(self) -> None:
        self._event_buffer.clear()

def _materialize(script_event: ScriptEvent, clock: Clock) -> ButtonEvent | TriggerEvent:
    t = clock()
    if script_event.type == "button":
        return ButtonEvent(
            time = t,
            code = str(script_event.code),
            device = ButtonDevice.SCRIPT,
            is_press = script_event.is_press,
        )
    elif script_event.type == "trigger":
        return TriggerEvent(
            time = t,
            device = ButtonDevice.SCRIPT,
            is_press = script_event.is_press,
            device_time_ms = round(t * 1000),
            system_time_s = t
        )
    else:
        raise RuntimeError(f"Unhandled ScriptEvent.type={script_event.type!r}")


class ScriptBuilder:
    def __init__(self):
        self._events: list[ScriptEvent] = []

    def press(self, key: str) -> "ScriptBuilder":
        self._events.append(ScriptEvent(type="button", code=key))
        return self

    def trigger(self, code: int = 4) -> "ScriptBuilder":
        self._events.append(ScriptEvent(type="trigger", code=str(code)))
        return self

    def repeat(self, n: int, fn: Callable[[ScriptBuilder], ScriptBuilder]) -> "ScriptBuilder":
        for _ in range(n):
            fn(self)
        return self

    def extend(self, events: list[ScriptEvent]) -> "ScriptBuilder":
        self._events.extend(events)
        return self

    def build(self) -> list[ScriptEvent]:
        return list(self._events)


def sequence(*fns: Callable[[ScriptBuilder], ScriptBuilder]):
    def apply(s: ScriptBuilder) -> ScriptBuilder:
        for fn in fns:
            fn(s)
        return s
    return apply


# The following helpers are for use with repeat() and sequence()
def fixation(s: ScriptBuilder):
    return s.press("space")

def feedback(s: ScriptBuilder):
    return s.press("space")

def respond_left(s: ScriptBuilder):
    return s.press("f")

def respond_right(s: ScriptBuilder):
    return s.press("j")

def respond_left_cedrus(s: ScriptBuilder):
    return s.press("0")

def respond_right_cedrus(s: ScriptBuilder):
    return s.press("2")

def send_scanner_trigger(s: ScriptBuilder):
    return s.trigger(4)

