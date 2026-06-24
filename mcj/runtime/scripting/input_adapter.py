from mcj.runtime.time import Clock
from mcj.runtime.input import InputAdapter, AdapterType
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
        clock: Clock,
        scheduler: ScriptScheduler
    ):
        self._clock = clock
        self._scheduler = scheduler
        self._event_buffer = []

    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.SCRIPTED

    def update(self) -> None:
        ready_events = self._scheduler.pop_ready_events()

        for ev in ready_events:
            self._event_buffer.append(
                _materialize(ev, self._clock)
            )

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

