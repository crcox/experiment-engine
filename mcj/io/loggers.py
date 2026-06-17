from __future__ import annotations

import json
from pathlib import Path
from typing import  Sequence, Callable

from abc import ABC, abstractmethod
from mcj.runtime.events import (
    EventRecorder,
    EventDict,
)

class BaseLogger(ABC):
    """
    Base class for append-only, cursor-based loggers.

    Assumes events are dicts produced by EventRecorder.

    All events are expected to include a "type" key.

    Subclasses consume an append-only event stream and persist
    new events incrementally without mutating the source.
    """

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self._last_written_index: int = 0

    def write_new(self, event_record: EventRecorder) -> None:
        """
        Write all events with types the logger instance is responsible for that
        have not yet written, then advance the cursor.

        """
        events = event_record.events()
        new_events = events[self._last_written_index :]

        attended = self._attend(new_events)

        if attended:
            self._write_records(attended)
            
        self._last_written_index = len(events)

    def _write_records(self, events: Sequence[EventDict]):
        with self.output_path.open("a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

    @abstractmethod
    def _attend(
        self,
        events: Sequence[EventDict]
    ) -> list[EventDict]:
        """
        Persist records to disk.

        Must be implemented by subclasses.
        Must not modify `events`.
        """
        raise NotImplementedError


class EventTypeLogger(BaseLogger):

    def __init__(self, output_path: Path, event_types: set[str]):
        super().__init__(output_path)
        self._event_types = event_types

    def _attend(self, events: Sequence[EventDict]) -> list[EventDict]:
        return [e for e in events if e.get("type") in self._event_types]


class SamplingLogger(BaseLogger):
    """
    Logger that writes every Nth occurrence of a single event type.

    Intended for high-frequency streams of instantaneous events (e.g., mouse position, eye tracking, electrophysiology).

    WARNING:
        Do not use for bounded or lifecycle-critical events
        (e.g., those defined in start/end pairs), as this may drop essential records.
    """
    def __init__(
        self,
        output_path: Path,
        event_type: str,
        every: int,
    ):
        super().__init__(output_path)

        if every <= 0:
            raise ValueError("Sampling rate must be positive")

        self._event_type = event_type
        self._every = every
        self._counter = 0

    def _attend(self, events: Sequence[EventDict]) -> list[EventDict]:
        result: list[EventDict] = []

        for e in events:
            if e.get("type") == self._event_type:
                self._counter += 1
                if self._counter % self._every == 0:
                    result.append(e)

        return result


class PredicateLogger(BaseLogger):
    """
    Logger that writes every event that satisfies a predicate function.

    Use this when you need custom event filtering. Note that:

        EventDict = dict[str, object]

    Instances of EventDict are derived from event classes, which all have at
    least `type` and `time` properties. 

    Advanced users may implement stateful predicates (e.g., time-based or
    count-based sampling) using closures. These patterns are intentionally not
    exposed as first-class loggers, as they require careful reasoning about
    correctness and the introduction of implicit, arbitrary state.

    For example, the behavior of SamplingLogger can be achieved with a
    predicate:

        def make_sampling_predicate(event_type: str, every: int):
            counter = 0

            def predicate(e):
                nonlocal counter

                if e.get("type") != event_type:
                    return False

                counter += 1
                return counter % every == 0

            return predicate

        PredicateLogger(path, predicate=make_sampling_predicate("mouse_move", 5))

    """

    def __init__(self, output_path: Path, predicate: Callable[[EventDict], bool]):
        super().__init__(output_path)
        self._predicate = predicate

    def _attend(self, events: Sequence[EventDict]) -> list[EventDict]:
        return [e for e in events if self._predicate(e)]
