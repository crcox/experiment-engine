from mcj.runtime.time import Clock
from mcj.runtime.keyboard import KeyboardAdapter
from mcj.runtime.input_events import ButtonEvent, ButtonDevice

from mcj.runtime.scripting.events import ScriptEvent


class KeyboardScriptDriver:
    """
    Drives a KeyboardAdapter using scripted events.

    Semantics identical to CedrusScriptDriver:
    - time=None → emit exactly ONE event per update()
    - time=float → emit ALL events whose time has elapsed
    """

    _adapter: KeyboardAdapter

    def __init__(
        self,
        clock: Clock,
        adapter: KeyboardAdapter,
    ):
        self._clock = clock
        self._adapter = adapter


    def handle(self, ev: ScriptEvent) -> None:
        now = self._clock()

        if ev.type == "button":
            event = ButtonEvent(
                time=now,
                code=str(ev.code),
                device=ButtonDevice.SCRIPT,
                is_press=True,
            )

            self._adapter.inject_event(event)

        elif ev.type == "trigger":
            pass

        else:
            raise RuntimeError(f"Unhandled ScriptEvent.type={ev.type!r}")
