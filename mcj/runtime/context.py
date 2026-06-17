from __future__ import annotations

from dataclasses import dataclass

from mcj.runtime.time import Clock
from mcj.plans.common import TaskPlan
from mcj.runtime.modes import Mode
from mcj.runtime.roles import RoleConfig
from mcj.runtime.events import EventRecorder
from mcj.runtime.input import InputManager, InputBackend
from typing import Mapping, Type, TypeVar

T = TypeVar("T", bound=TaskPlan)

@dataclass(frozen=True)
class SessionContext:
    """
    Runtime context for a single experimental session.

    Bundles all session-scoped runtime authorities:
    - time
    - truth (event recording)
    - immutable TaskPlans
    """
    
    _plans: Mapping[str, TaskPlan]
    clock: Clock
    input: InputManager
    input_backend: InputBackend
    recorder: EventRecorder

    def now(self) -> float:
        return self.clock()

    def get_plan(self, task_code: str) -> TaskPlan:
        try:
            return self._plans[task_code]
        except KeyError:
            raise KeyError(
                f"No plan registered for task={task_code!r}"
            )

    def get_plan_typed(self, task_code: str, cls: Type[T]) -> T:
        plan = self.get_plan(task_code)
        assert isinstance(plan, cls)
        return plan


@dataclass(frozen=True)
class RuntimeContext:
    ctx: SessionContext
    role_cfg: RoleConfig
    mode: Mode

