from dataclasses import dataclass
from typing import Generic, TypeVar

ActionT = TypeVar("ActionT")

@dataclass
class ActionRef(Generic[ActionT]):
    value: ActionT | None = None 

    def get(self) -> ActionT | None:
        return self.value

    def set(self, action: ActionT | None) -> None:
        self.value = action

    def clear(self) -> None:
        self.value = None
