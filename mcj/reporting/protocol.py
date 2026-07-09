from typing import Protocol
from typing import Any

class SessionTranslator(Protocol):
    def consume(self, event: dict[str, Any]) -> None:
        ...

    def finalize(self) -> None:
        ...
