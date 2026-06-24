from typing import Callable, Literal

from mcj.runtime.scripting.events import ScriptEvent

class ScriptBuilder:
    def __init__(self):
        self._events: list[ScriptEvent] = []
        self._t: float | None = None

    def wait(self, dt: float) -> "ScriptBuilder":
        if self._t is None:
            self._t = 0.0

        self._t += dt
        return self

    def at(self, t: float) -> "ScriptBuilder":
        self._t = t
        return self

    def now(self) -> "ScriptBuilder":
        self._t = None
        return self

    def after(self, dt: float) -> "ScriptBuilder":
        return self.wait(dt)

    def press(self, key: str, target: Literal["keyboard", "cedrus"] | None = None) -> "ScriptBuilder":
        self._append(target=target, type="button", code=key, is_press=True)
        return self

    def trigger(self, code: int = 4, target: Literal["keyboard", "cedrus"] | None = None) -> "ScriptBuilder":
        self._append(target=target, type="trigger", code=str(code), is_press=True)
        return self

    def repeat(self, n: int, fn: Callable[["ScriptBuilder"], "ScriptBuilder"]) -> "ScriptBuilder":
        for _ in range(n):
            fn(self)
        return self

    def extend(self, events: list[ScriptEvent]) -> "ScriptBuilder":
        self._events.extend(events)
        return self

    def build(self) -> list[ScriptEvent]:
        return list(self._events)

    def _append(self, type: Literal["button", "trigger"], code: str, is_press: bool, target: Literal["keyboard", "cedrus"] | None):
        self._events.append(
            ScriptEvent(
                time=self._t,
                type=type,
                code=code,
                is_press=is_press,
                target=target,
            )
        )



