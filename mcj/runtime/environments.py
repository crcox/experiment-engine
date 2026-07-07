from enum import Enum

class Environment(str, Enum):
    LOCAL = "local"
    SCANNER = "scanner"

    @property
    def allows_feedback(self) -> bool:
        return self in {
            Environment.LOCAL,
        }

    @property
    def allows_definition(self) -> bool:
        return self in {
            Environment.LOCAL,
        }

    @property
    def requires_alignment(self) -> bool:
        return self in {
            Environment.SCANNER,
        }

    @property
    def waits_for_trigger(self) -> bool:
        return self in {
            Environment.SCANNER,
        }
