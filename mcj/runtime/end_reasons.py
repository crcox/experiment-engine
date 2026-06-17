from enum import Enum

class EndReason(str, Enum):
    ABORTED="aborted"
    COMPLETE="complete"
    FAIL="fail"
    ERROR="error"
    INVALID_INPUT="invalid_input"
    TIMEOUT="timeout"

