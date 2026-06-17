from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Callable, Any

from mcj.runtime.input_events import ButtonEvent
from mcj.runtime.states import State

from mcj.tasks.criterion_judgment.actions import CriterionJudgmentAction as Action

class EventMapping(ABC):
    @abstractmethod
    def interpret(self, event: ButtonEvent) -> str | Action | None:
        pass

class NoOpMapping(EventMapping):
    def interpret(self, event: ButtonEvent) ->  None:
        return None

@dataclass(frozen=True)
class KeyPressMapping(EventMapping):
    codes: set[str]

    def interpret(self, event: ButtonEvent) -> str | None:
        if event.code in self.codes:
            return event.code
        return None

@dataclass(frozen=True)
class AdvanceMapping(EventMapping):
    codes: set[str]

    def interpret(self, event: ButtonEvent) -> Action | None:
        if event.code in self.codes:
            return Action.ADVANCE
        return None


EventMappingFactory = Callable[[Any], EventMapping]
EventMappingByState = Mapping[State, EventMappingFactory]
