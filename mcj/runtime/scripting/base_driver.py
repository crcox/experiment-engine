from typing import Protocol

from mcj.runtime.scripting.events import ScriptEvent


class ScriptDriver(Protocol):
    """
    Base class for all script-driven input simulators.

    Subclasses implement `_emit()` to define where events go.
    """

    def handle(self, ev: ScriptEvent) -> None:
        """
        Implement in subclass to send event to the appropriate target.
        """
        ...

