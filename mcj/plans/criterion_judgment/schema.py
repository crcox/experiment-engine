from __future__ import annotations

from mcj.plans.common import TaskPlan, BlockPlan
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

class CJCondition(str, Enum):
    DOMAIN="domain"
    SIZE="size"
    DANGER="danger"
    ORTHOGRAPHY="orthography"

    @property
    def requires_definition(self):
        return self in {
            CJCondition.SIZE,
            CJCondition.DANGER,
        }

class CJResponse(str, Enum):
    YES="yes"
    NO="no"

class CJResponseSide(str, Enum):
    LEFT="left"
    RIGHT="right"

class Domain(str, Enum):
    LIVING = "living"
    NONLIVING = "nonliving"


class Size(str, Enum):
    BIG = "big"
    SMALL = "small"

class Danger(str, Enum):
    DANGEROUS = "dangerous"
    SAFE = "safe"


class Orthography(str, Enum):
    UPPER = "uppercase"
    LOWER = "lowercase"

RESPONSE_TO_ATTRIBUTE_BY_CONDITION = {
    CJCondition.DOMAIN: {
        CJResponse.YES: Domain.LIVING,
        CJResponse.NO:  Domain.NONLIVING
    },
    CJCondition.SIZE: {
        CJResponse.YES: Size.SMALL,
        CJResponse.NO:  Size.BIG
    },
    CJCondition.DANGER: {
        CJResponse.YES: Danger.DANGEROUS,
        CJResponse.NO:  Danger.SAFE
    },
    CJCondition.ORTHOGRAPHY: {
        CJResponse.YES: Orthography.UPPER,
        CJResponse.NO:  Orthography.LOWER
    },
}

@dataclass(frozen=True)
class CJTrial:
    word: str
    domain: Domain
    size: Size
    danger: Danger
    orthography: Orthography

    def expected_response(self, condition: CJCondition) -> CJResponse:

        if condition == CJCondition.DOMAIN:
            return CJResponse.YES if self.domain == Domain.LIVING else CJResponse.NO

        elif condition == CJCondition.SIZE:
            return CJResponse.YES if self.size == Size.SMALL else CJResponse.NO

        elif condition == CJCondition.DANGER:
            return CJResponse.YES if self.danger == Danger.DANGEROUS else CJResponse.NO

        elif condition == CJCondition.ORTHOGRAPHY:
            return CJResponse.YES if self.orthography == Orthography.UPPER else CJResponse.NO


@dataclass(frozen=True)
class CJBlockPlan(BlockPlan):
    """
    Immutable specification of a single block's stimulus layout.

    A BlockPlan captures all block-level randomness and design intent
    required to reconstruct the logical world state of a block.
    """

    block_index: int
    condition: CJCondition
    trials: Sequence[CJTrial]

    @property
    def ntrials(self) -> int:
        return len(self.trials)


@dataclass(frozen=True)
class CJPlan(TaskPlan):
    """
    Complete immutable plan for running MCJ
    for a single subject in a single session.
    """
    subject_id: int | None
    blocks: Sequence[CJBlockPlan]
    left_response: CJResponse

    @property
    def nblocks(self) -> int:
        return len(self.blocks)

