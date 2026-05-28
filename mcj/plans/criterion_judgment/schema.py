from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


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
    UPPER = "upper"
    LOWER = "lower"


class CriterionJudgmentCondition(str, Enum):
    DOMAIN="domain"
    SIZE="size"
    DANGER="danger"
    ORTHOGRAPHY="orthography"


@dataclass(frozen=True)
class CriterionJudgmentTrial:
    word: str
    domain: Domain
    size: Size
    danger: Danger
    orthography: Orthography


@dataclass(frozen=True)
class CriterionJudgmentBlockPlan:
    """
    Immutable specification of a single block's stimulus layout.

    A BlockPlan captures all block-level randomness and design intent
    required to reconstruct the logical world state of a block.
    """

    block_index: int
    condition: CriterionJudgmentCondition
    trials: Sequence[CriterionJudgmentTrial]


@dataclass(frozen=True)
class CriterionJudgmentPlan:
    """
    Complete immutable plan for running Sequence‑MTS
    for a single subject in a single session.
    """
    subject_id: int
    blocks: list[CriterionJudgmentBlockPlan]

