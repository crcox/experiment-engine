from typing import Literal, TypedDict, TypeGuard

from mcj.runtime.event_types import EventType
from mcj.runtime.events import EventDict

class BlockExecutionStartEvent(TypedDict):
    type: Literal["block_execution_start"]
    time: float
    index: int

def is_block_execution_start_event(
        event: EventDict,
    ) -> TypeGuard[BlockExecutionStartEvent]:
    return event.get("type") == EventType.BLOCK_EXECUTION_START.value

class BlockExecutionEndEvent(TypedDict):
    type: Literal["block_execution_end"]
    time: float
    index: int

def is_block_execution_end_event(
        event: EventDict,
    ) -> TypeGuard[BlockExecutionEndEvent]:
    return event.get("type") == EventType.BLOCK_EXECUTION_END.value

class TrialStartEvent(TypedDict):
    type: Literal["trial_start"]
    time: float
    index: int

def is_trial_start_event(
        event: EventDict,
    ) -> TypeGuard[TrialStartEvent]:
    return event.get("type") == EventType.TRIAL_START.value

class TrialEndEvent(TypedDict):
    type: Literal["trial_end"]
    time: float
    reason: str
    cause: str

def is_trial_end_event(
        event: EventDict,
    ) -> TypeGuard[TrialEndEvent]:
    return event.get("type") == EventType.TRIAL_END.value

