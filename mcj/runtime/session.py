from dataclasses import dataclass
from typing import Callable

from mcj.runtime.environments import Environment
from mcj.runtime.session_context import SessionContext

@dataclass
class SessionRuntime:
    ctx: SessionContext
    environment: Environment
    drivers: 
    on_block_start: tuple[Callable, ...]
    on_block_end: tuple[Callable, ...]

