from enum import Enum

class TrialOutcome(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"
