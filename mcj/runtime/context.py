from __future__ import annotations

from dataclasses import dataclass
from psychopy.core import Clock

from mcj.plans.common import TaskPlan
from mcj.runtime.events import EventRecorder
from typing import Mapping


@dataclass
class SessionContext:
    """
    Runtime context for a single experimental session.

    Bundles all session-scoped runtime authorities:
    - time
    - truth (event recording)
    - immutable TaskPlans
    """
    
    def __init__(
        self,
        *,
        plans: Mapping[str, Mapping[str, TaskPlan]],
        clock: Clock,
        recorder: EventRecorder
    ):
        self._plans = plans
        self.clock: Clock = clock
        self.recorder: EventRecorder = recorder

    def now(self) -> float:
        return self.clock.getTime()

    def get_plan(self, task_code: str, *, role: str):
        try:
            return self._plans[task_code][role]
        except KeyError:
            raise KeyError(
                f"No plan registered for task={task_code!r}, role={role!r}"
            )
