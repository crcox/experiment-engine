from mcj.runtime.scripting.events import ScriptEvent

from mcj.adapters.pyxid2.mock import MockXidDevice


class CedrusScriptDriver:
    """
    Drives a MockXidDevice using a scripted sequence of events.

    Semantics:
    - time=None → emit exactly ONE event per update() call (sequential mode)
    - time=float → emit ALL events whose scheduled time has elapsed (timed mode)
    - never mixes untimed and timed events in a single update
    """

    _device: MockXidDevice

    def __init__(
        self,
        device: MockXidDevice,
    ):
        self._device = device

    def handle(self, ev: ScriptEvent) -> None:
        """Translate ScriptEvent → device action."""
        if ev.target != "cedrus":
            return

        if ev.type == "button":
            # Cedrus expects integer key codes
            self._device.simulate_button(int(ev.code))

        elif ev.type == "trigger":
            self._device.simulate_trigger()

        else:
            raise RuntimeError(f"Unhandled ScriptEvent.type={ev.type!r}")
