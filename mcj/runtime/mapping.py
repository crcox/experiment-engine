from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Callable, Any, TypeVar, Generic

from mcj.runtime.session import SessionRuntime
from mcj.runtime.input_events import ButtonEvent
from mcj.runtime.states import State

ActionT = TypeVar("ActionT")

class ActionMapping(ABC, Generic[ActionT]):
    @abstractmethod
    def interpret(self, event: ButtonEvent) -> ActionT | None:
        pass

class NoOpMapping(ActionMapping[ActionT]):
    def interpret(self, event: ButtonEvent) ->  None:
        return None

@dataclass(frozen=True)
class KeyToActionMapping(ActionMapping[ActionT], Generic[ActionT]):
    mapping: dict[str, ActionT]

    def interpret(self, event: ButtonEvent) -> ActionT | None:
        print(f"event.code={event.code}, mapping={self.mapping}")
        return self.mapping.get(event.code)


ActionMappingFactory = Callable[[Any], ActionMapping[ActionT]]
ActionMappingByState = Mapping[State, Callable[[Any], ActionMapping[ActionT]]]

def constant_mapping(mapping: ActionMapping[ActionT]) -> ActionMappingFactory[ActionT]:
    return lambda _: mapping

def key_mapping(mapping: dict[str, ActionT]) -> ActionMappingFactory[ActionT]:
    return constant_mapping(KeyToActionMapping(mapping))

def no_op() -> ActionMappingFactory[ActionT]:
    return constant_mapping(NoOpMapping())

def dynamic_mapping(builder: Callable[[SessionRuntime], ActionMapping[ActionT]]) -> ActionMappingFactory[ActionT]:
    return lambda run_ctx: builder(run_ctx)
