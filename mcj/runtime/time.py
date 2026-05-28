from psychopy.core import Clock

class Timer:
    def __init__(self, session_clock: Clock):
        self._clock: Clock = session_clock
        self._t0: float = session_clock.getTime()

    def elapsed(self) -> float:
        return self._clock.getTime() - self._t0

    def elapsed_at(self, timestamp: float) -> float:
        return timestamp - self._t0

    def reset(self):
        self._t0 = self._clock.getTime()
