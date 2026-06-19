from dataclasses import dataclass

from mcj.runtime.modes import Mode
from mcj.runtime.session_context import SessionContext

@dataclass(frozen=True)
class SessionRuntime:
    ctx: SessionContext
    mode: Mode

