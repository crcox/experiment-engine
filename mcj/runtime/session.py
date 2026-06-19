from dataclasses import dataclass

from mcj.runtime.environments import Environment
from mcj.runtime.session_context import SessionContext

@dataclass(frozen=True)
class SessionRuntime:
    ctx: SessionContext
    environment: Environment

