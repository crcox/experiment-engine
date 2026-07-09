from enum import Enum

class CJEventType(Enum):
    DEFINITION_START="definition_start" 
    DEFINITION_END="definition_end"
    PROMPT_START="prompt_start"
    PROMPT_END="prompt_end"
    CONDITION_SET="condition_set"
    STIMULUS_ONSET="stimulus_onset"
    ACTION="action"
    RESPONSE="response"
    RESPONSE_MARK="response_mark"
    TASK_START="task_start"
    TASK_END="task_end"
    STIMULUS_START="stimulus_start"
    STIMULUS_END="stimulus_end"
    FEEDBACK_START="feedback_start"
    FEEDBACK_END="feedback_end"
