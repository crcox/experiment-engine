from typing import Callable

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

    def press(self, key: str) -> "ScriptBuilder":
        self._append(type="button", code=key, is_press=True)
        return self

    def trigger(self, code: int = 4) -> "ScriptBuilder":
        self._append(type="trigger", code=str(code), is_press=True)
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

    def _append(self, type, code, is_press=True):
        self._events.append(
            ScriptEvent(
                time=self._t,
                type=type,
                code=code,
                is_press=is_press,
            )
        )


def sequence(*fns: Callable[[ScriptBuilder], ScriptBuilder]):
    def apply(s: ScriptBuilder) -> ScriptBuilder:
        for fn in fns:
            fn(s)
        return s
    return apply


