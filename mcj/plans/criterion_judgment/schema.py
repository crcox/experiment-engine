from __future__ import annotations

from mcj.plans.common import TaskPlan, BlockPlan
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

class CriterionJudgmentCondition(str, Enum):
    DOMAIN="domain"
    SIZE="size"
    DANGER="danger"
    ORTHOGRAPHY="orthography"

    @property
    def requires_definition(self):
        return self in {
            CriterionJudgmentCondition.SIZE,
            CriterionJudgmentCondition.DANGER,
        }

class CriterionJudgmentResponse(str, Enum):
    YES="yes"
    NO="no"

class CriterionJudgmentResponseSide(str, Enum):
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
    CriterionJudgmentCondition.DOMAIN: {
        CriterionJudgmentResponse.YES: Domain.LIVING,
        CriterionJudgmentResponse.NO:  Domain.NONLIVING
    },
    CriterionJudgmentCondition.SIZE: {
        CriterionJudgmentResponse.YES: Size.SMALL,
        CriterionJudgmentResponse.NO:  Size.BIG
    },
    CriterionJudgmentCondition.DANGER: {
        CriterionJudgmentResponse.YES: Danger.DANGEROUS,
        CriterionJudgmentResponse.NO:  Danger.SAFE
    },
    CriterionJudgmentCondition.ORTHOGRAPHY: {
        CriterionJudgmentResponse.YES: Orthography.UPPER,
        CriterionJudgmentResponse.NO:  Orthography.LOWER
    },
}

@dataclass(frozen=True)
class CriterionJudgmentTrial:
    word: str
    domain: Domain
    size: Size
    danger: Danger
    orthography: Orthography

    def expected_response(self, condition: CriterionJudgmentCondition) -> CriterionJudgmentResponse:

        if condition == CriterionJudgmentCondition.DOMAIN:
            return CriterionJudgmentResponse.YES if self.domain == Domain.LIVING else CriterionJudgmentResponse.NO

        elif condition == CriterionJudgmentCondition.SIZE:
            return CriterionJudgmentResponse.YES if self.size == Size.SMALL else CriterionJudgmentResponse.NO

        elif condition == CriterionJudgmentCondition.DANGER:
            return CriterionJudgmentResponse.YES if self.danger == Danger.DANGEROUS else CriterionJudgmentResponse.NO

        elif condition == CriterionJudgmentCondition.ORTHOGRAPHY:
            return CriterionJudgmentResponse.YES if self.orthography == Orthography.UPPER else CriterionJudgmentResponse.NO


@dataclass(frozen=True)
class CriterionJudgmentBlockPlan(BlockPlan):
    """
    Immutable specification of a single block's stimulus layout.

    A BlockPlan captures all block-level randomness and design intent
    required to reconstruct the logical world state of a block.
    """

    block_index: int
    condition: CriterionJudgmentCondition
    trials: Sequence[CriterionJudgmentTrial]

    @property
    def ntrials(self) -> int:
        return len(self.trials)


@dataclass(frozen=True)
class CriterionJudgmentPlan(TaskPlan):
    """
    Complete immutable plan for running MCJ
    for a single subject in a single session.
    """
    subject_id: int | None
    blocks: Sequence[CriterionJudgmentBlockPlan]
    left_response: CriterionJudgmentResponse

    @property
    def nblocks(self) -> int:
        return len(self.blocks)

