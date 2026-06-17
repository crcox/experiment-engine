from abc import ABC, abstractmethod
from typing import Sequence
from mcj.runtime.input_events import ButtonEvent, TriggerEvent

class InputAdapter(ABC):

    @abstractmethod
    def poll(self) -> Sequence[ButtonEvent | TriggerEvent]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
