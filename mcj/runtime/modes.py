from enum import Enum

class Mode(str, Enum):
    PRACTICE = "practice"
    SCANNER = "scanner"

    @property
    def allows_feedback(self) -> bool:
        return self != Mode.SCANNER

    @property
    def allows_definition(self) -> bool:
        return self != Mode.SCANNER
