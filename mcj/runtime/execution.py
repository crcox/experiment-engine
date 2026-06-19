from __future__ import annotations

from typing import TypeVar, Generic
from dataclasses import dataclass

from mcj.runtime.roles import RoleConfig
from mcj.runtime.session import SessionRuntime

ActionT = TypeVar("ActionT")

@dataclass(frozen=True)
class ExecutionContext(Generic[ActionT]):
    session: SessionRuntime
    role_cfg: RoleConfig[ActionT]

