from typing import Literal, TypeGuard, TypedDict

from mcj.runtime.events import EventDict
from mcj.tasks.criterion_judgment.event_types import CJEventType

class ConditionSetEvent(TypedDict):
    type: Literal["condition_set"]
    time: float
    condition: Literal["domain", "size", "danger", "orthography"]

def is_condition_set_event(
        event: EventDict,
    ) -> TypeGuard[ConditionSetEvent]:
    return event.get("type") == CJEventType.CONDITION_SET.value

class StimulusStartEvent(TypedDict):
    type: Literal["stimulus_start"]
    time: float
    word: str
    domain: Literal["living", "nonliving"]
    size: Literal["big", "small"]
    danger: Literal["safe", "dangerous"]
    orthography: Literal["uppercase", "lowercase"]


def is_stimulus_start_event(
        event: EventDict,
    ) -> TypeGuard[StimulusStartEvent]:
    return event.get("type") == CJEventType.STIMULUS_START.value

class StimulusEndEvent(TypedDict):
    type: Literal["stimulus_end"]
    time: float
    reason: str
    cause: str

def is_stimulus_end_event(
        event: EventDict,
    ) -> TypeGuard[StimulusEndEvent]:
    return event.get("type") == CJEventType.STIMULUS_END.value

class StimulusOnsetEvent(TypedDict):
    type: Literal["stimulus_onset"]
    time: float

def is_stimulus_onset_event(
        event: EventDict,
    ) -> TypeGuard[StimulusOnsetEvent]:
    return event.get("type") == CJEventType.STIMULUS_ONSET.value

class ResponseEvent(TypedDict):
    type: Literal["response"]
    time: float
    response: str

def is_response_event(
        event: EventDict,
    ) -> TypeGuard[ResponseEvent]:
    return event.get("type") == CJEventType.RESPONSE.value

