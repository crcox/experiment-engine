from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, auto
from typing import Sequence, Type, TypeVar

from mcj.runtime.input_events import ButtonEvent, TriggerEvent

class InputMode(Enum):
    REAL = "real"
    SIMULATED_DIRECT = "simulated_direct"
    SIMULATED_DEVICE = "simulated_device"

    @property
    def requires_script(self) -> bool:
        return self in {
            InputMode.SIMULATED_DIRECT,
            InputMode.SIMULATED_DEVICE,
        }


class InputChannel(Enum):
    KEYBOARD = auto()
    CEDRUS = auto()

class InputAdapter(ABC):

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def pop_events(self) -> Sequence[ButtonEvent | TriggerEvent]:
        pass

    @abstractmethod
    def peek_events(self) -> Sequence[ButtonEvent | TriggerEvent]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


T = TypeVar("T", bound=InputAdapter)

class InputManager:
    _adapters: Sequence[InputAdapter]
    _buffer: deque[ButtonEvent | TriggerEvent]

    def __init__(self, adapters: Sequence[InputAdapter]):
        self._adapters = adapters
        self._buffer = deque()

    def update(self) -> None:
        for adapter in self._adapters:
            adapter.update()
            self._buffer.extend(adapter.pop_events())

        self._buffer = deque(sorted(self._buffer, key=lambda x: x.time))


    def peek_events(self) -> Sequence[ButtonEvent | TriggerEvent]:
        return list(self._buffer)

    def pop_event(self) -> ButtonEvent | TriggerEvent | None:
        if not self._buffer:
            return None

        return self._buffer.popleft()

    def pop_events(self) -> Sequence[ButtonEvent | TriggerEvent]:
        events = list(self._buffer)
        self._buffer.clear()
        return events

    def inject_event(self, event: ButtonEvent | TriggerEvent) -> None:
        self._buffer.append(event)


    def clear(self):
        for adapter in self._adapters:
            adapter.clear()

        self._buffer.clear()

    def require_adapter(self, adapter_cls: Type[T]) -> T:
        for a in self._adapters:
            if isinstance(a, adapter_cls):
                return a

        raise RuntimeError(f"No adapter of class {adapter_cls} was registered with InputManager.")

    def has_adapter(self, adapter_cls: Type[T]) -> bool:
        return any(isinstance(a, adapter_cls) for a in self._adapters)

    def get_adapters(self) -> Sequence[InputAdapter]:
        return self._adapters

    def was_pressed(self, code: str) -> bool:
        for event in self._buffer:
            if isinstance(event, ButtonEvent):
                if event.code == code:
                    return True

        return False
