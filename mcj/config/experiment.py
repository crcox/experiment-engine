from __future__ import annotations

from mcj.runtime.roles import PlanRole
from dataclasses import dataclass

EXPERIMENT_NAME: str = "Multi-Criterion Judgment Task"


@dataclass(frozen=True)
class SessionConfig:
    num_blocks: int
    show_feedback: bool

CONFIG_BY_ROLE = {
    PlanRole.PRACTICE: SessionConfig(num_blocks=4, show_feedback=True),
    PlanRole.MAIN: SessionConfig(num_blocks=8, show_feedback=False)
}
