from typing import Any

from psychopy.hardware.keyboard import KeyPress

from mcj.adapters.psychopy.protocols import KeyboardLike


class MockKeyboard(KeyboardLike):
    def getKeys(
        self,
        keyList: list[Any] | None = None,
        ignoreKeys: list[Any] | None = None,
        waitRelease: bool = True,
        clear: bool = True,
    ) -> list[KeyPress]:
        return []

    def clearEvents(self, eventType: Any = None) -> None:
        pass
