from dataclasses import dataclass
from typing import Callable

from mcj.runtime.environments import Environment
from mcj.runtime.scripting.scheduler import ScriptScheduler
from mcj.runtime.scripting.base_driver import ScriptDriver
from mcj.runtime.session_context import SessionContext

@dataclass
class SessionRuntime:
    ctx: SessionContext
    environment: Environment
    scheduler: ScriptScheduler | None
    drivers: tuple[ScriptDriver, ...]
    on_block_start: tuple[Callable, ...] | None
    on_block_end: tuple[Callable, ...] | None

    def maybe_step_simulation(self) -> None:
        if self.scheduler is None:
            return

        if not self.drivers:
            return

        events = self.scheduler.pop_ready_events()

        for ev in events:
            for driver in self.drivers:
                driver.handle(ev)
