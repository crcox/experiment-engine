from typing import TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from mcj.runtime.states import State
from mcj.runtime.termination import (
    TerminationCondition,
    ActionOrTimeoutTermination,
    TimeTermination
)
from mcj.runtime.mapping import ActionMappingByState

ActionT = TypeVar("ActionT")

class TaskProfile(str, Enum):
    MAIN="main"
    PRACTICE="practice"
    DEV="dev"

@dataclass(frozen=True)
class FeedbackStimulusConfig:
    text: str
    color: str

@dataclass(frozen=True)
class FeedbackConfig:
    duration_seconds: float | None
    stimulus_correct: FeedbackStimulusConfig 
    stimulus_incorrect: FeedbackStimulusConfig 
    stimulus_timeout: FeedbackStimulusConfig 

@dataclass(frozen=True)
class ResponseMarkConfig:
    enabled: bool = False
    color: str = "lightgrey"
    height: float = 0.03
    y_offset: float = -0.1


@dataclass(frozen=True)
class TaskProfileConfig(Generic[ActionT]):
    termination_by_state: Mapping[State, TerminationCondition[ActionT]]
    action_mapping_by_state: ActionMappingByState[ActionT]
    prompt_duration_seconds: float | None
    fixation_duration_seconds: float | None
    stimulus_duration_seconds: float | None
    feedback: FeedbackConfig | None
    response_mark : ResponseMarkConfig | None

    @property
    def has_feedback_cfg(self) -> bool:
        return self.feedback is not None

    def require_feedback(self) -> FeedbackConfig:
        if self.feedback is None:
            raise RuntimeError("Subsequent operations required feedback to be defined")
        return self.feedback

    def should_show_response_mark(
        self,
        state: State
    ) -> bool:
        return (
            self.response_mark is not None
            and isinstance(self.termination_by_state[state], (TimeTermination, ActionOrTimeoutTermination))
        )

