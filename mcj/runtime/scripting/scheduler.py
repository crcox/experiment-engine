from collections import deque
from typing import Sequence

from mcj.runtime.exceptions import ScriptExhaustedError
from mcj.runtime.scripting.events import ScriptEvent
from mcj.runtime.time import Clock


class ScriptScheduler:

    def __init__(self, clock: Clock, script: Sequence[ScriptEvent]):
        self._clock = clock
        self._script = deque(script)
        self._start_time = None

    def pop_ready_events(self) -> list:
        now = self._clock()

        if self._start_time is None:
            self._start_time = now

        elapsed = now - self._start_time

        if not self._script:
            raise ScriptExhaustedError

        events = []

        next_event = self.peek_script_event()

        # Untimed → one only
        if next_event.time is None:
            events.append(self.pop_script_event())
            return events

        # Timed → all due
        while self._script:
            next_event = self.peek_script_event()

            if next_event.time is None:
                break

            if next_event.time > elapsed:
                break

            events.append(self.pop_script_event())

        return events

    def pop_script_event(self) -> ScriptEvent:
        return self._script.popleft()

    def peek_script_event(self, index: int = 0) -> ScriptEvent:
        """
        Return a script event without modifying self._script.
        """
        return self._script[index]

    @property
    def is_finished(self) -> bool:
        return not self._script

    @property
    def remaining_events(self) -> int:
        return len(self._script)

    @property
    def reset(self):
        self._start_time = None
