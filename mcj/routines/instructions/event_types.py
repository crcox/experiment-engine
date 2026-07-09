from enum import Enum

class InstructionsEventType(Enum):
    INSTRUCTION_START="instruction_start"
    INSTRUCTION_END="instruction_end"
    SLIDE_START="slide_start"
    SLIDE_END="slide_end"
