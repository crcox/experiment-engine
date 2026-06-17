from __future__ import annotations

from dataclasses import dataclass
from mcj.runtime.exceptions import DataContractError
from typing import TypeAlias, Mapping

@dataclass(frozen=True)
class WordMetadata:
    word: str
    domain: str
    size: str
    danger: str
    orthography: str

    def __post_init__(self):
        if not self.domain in ["living", "nonliving"]:
            raise DataContractError(f"Invalid domain code: {self.domain!r} for word {self.word!r}.")

        if not self.size in ["big", "small"]:
            raise DataContractError(f"Invalid size code: {self.size!r} for word {self.word!r}.")

        if not self.danger in ["safe", "dangerous"]:
            raise DataContractError(f"Invalid danger code: {self.danger!r} for word {self.word!r}.")

        if not self.orthography in ["uppercase", "lowercase"]:
            raise DataContractError(f"Invalid orthography code: {self.orthography!r} for word {self.word!r}.")

WordTable: TypeAlias = Mapping[str, WordMetadata]

