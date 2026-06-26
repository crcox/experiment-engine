from mcj.runtime.time import Clock
from mcj.runtime.input import InputAdapter
from mcj.runtime.input_events import ButtonEvent, TriggerEvent, ButtonDevice

from mcj.runtime.scripting.scheduler import ScriptScheduler
from mcj.runtime.scripting.events import ScriptEvent

class ScriptedInputAdapter(InputAdapter):
    _clock: Clock
    _scheduler: ScriptScheduler
    _event_buffer: list[ButtonEvent | TriggerEvent]
    _start_time: float | None = None

    def __init__(
        self,
    ):
        self._event_buffer = []

    def update(self) -> None:
        # No-op: this adapter no longer generates events
        pass

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

