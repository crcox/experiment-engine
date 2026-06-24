from __future__ import annotations

from typing import TypeVar, Generic
from dataclasses import dataclass

from mcj.runtime.profiles import TaskProfileConfig
from mcj.runtime.session import SessionRuntime

ActionT = TypeVar("ActionT")

@dataclass(frozen=True)
class ExecutionContext(Generic[ActionT]):
    session: SessionRuntime
    profile_cfg: TaskProfileConfig[ActionT]


