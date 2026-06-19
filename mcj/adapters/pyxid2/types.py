from typing import Generic, Protocol, TypedDict, TypeVar, Any
from dataclasses import dataclass

from mcj.runtime.time import Clock

class XidEvent(TypedDict):
    port: int
    key: int
    pressed: bool
    time: int

T = TypeVar("T")

@dataclass(frozen=True)
class Stamped(Generic[T]):
    payload: T
    system_time: float

class XidDeviceLike(Protocol):
    def poll_for_response(self) -> None: ...
    def get_next_response(self) -> Any | None: ...
    def clear_response_queue(self) -> None: ...
    def response_queue_size(self) -> int: ...
    def reset_timer(self) -> None: ...

def stamp_event(evt: XidEvent, now: Clock) -> Stamped[XidEvent]:
    return Stamped(
        payload=evt,
        system_time=now()
    )
