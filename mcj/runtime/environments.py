from enum import Enum

class Environment(str, Enum):
    LOCAL = "local"
    SCANNER = "scanner"

    @property
    def allows_feedback(self) -> bool:
        return self != Environment.SCANNER

    @property
    def allows_definition(self) -> bool:
        return self != Environment.SCANNER
