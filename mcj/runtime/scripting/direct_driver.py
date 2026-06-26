from mcj.runtime.time import Clock
from mcj.runtime.input import InputManager
from mcj.runtime.input_events import ButtonEvent, TriggerEvent, ButtonDevice
from mcj.runtime.scripting.events import ScriptEvent


class DirectScriptDriver:
    """
    Directly injects ScriptEvents into the InputManager.

    Bypasses all devices and adapters. Used for fast, pure simulation.
    """

    def __init__(
        self,
        clock: Clock,
        input_manager: InputManager,
    ):
        self._clock = clock
        self._input = input_manager

    def handle(self, ev: ScriptEvent) -> None:
        t = self._clock()

        if ev.type == "button":
            event = ButtonEvent(
                time=t,
                code=str(ev.code),
                device=ButtonDevice.SCRIPT,
                is_press=ev.is_press,
            )
            self._input.inject_event(event)

        elif ev.type == "trigger":
            event = TriggerEvent(
                time=t,
                device=ButtonDevice.SCRIPT,
                is_press=ev.is_press,
                device_time_ms=round(t * 1000),
                system_time_s=t,
            )
            self._input.inject_event(event)

        else:
            raise RuntimeError(f"Unhandled ScriptEvent.type={ev.type!r}")
