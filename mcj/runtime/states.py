from enum import Enum, auto
from typing import Union

class InstructionState(Enum):
    INSTRUCTION = auto()
    DONE = auto()

class DefinitionState(Enum):
    DEFINITION = auto()
    DONE = auto()

class PromptState(Enum):
    PROMPT = auto()
    DONE = auto()

class TrialState(Enum):
    FIXATION = auto()
    STIMULUS = auto()
    FEEDBACK = auto()
    DONE = auto()

State = Union[
    InstructionState,
    PromptState,
    DefinitionState,
    TrialState
]
