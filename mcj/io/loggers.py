from __future__ import annotations

import json
from pathlib import Path
from typing import cast, Sequence, Union
from abc import ABC, abstractmethod
from mcj.runtime.events import (
    EventRecorder,
    Event,
    MouseClickEvent,
    MousePositionEvent,
    BlockStartEvent,
    BlockAbortEvent,
    BlockEndEvent,
    TrialStartEvent,
    TrialAbortEvent,
    TrialEndEvent
)

SessionEvent = Union[
    BlockStartEvent,
    BlockAbortEvent,
    BlockEndEvent,
    TrialStartEvent,
    TrialAbortEvent,
    TrialEndEvent
]


class BaseLogger(ABC):
    """
    Base class for append-only, cursor-based loggers.

    Subclasses consume an append-only event stream and persist
    new events incrementally without mutating the source.
    """

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self._event_types = list[str]
        self._last_written_index: int = 0

    def write_new(self, event_record: EventRecorder) -> None:
        """
        Write all events with types the logger instance is responsible for that
        have not yet written, then advance the cursor.

        """
        events = event_record.events()
        new_events = events[self._last_written_index :]
        attended_new_events = self._attend(new_events)

        if attended_new_events:
            self._write_records(attended_new_events)
            self._last_written_index = len(events)

    def _write_records(self, events):
        with self.output_path.open("a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

    @abstractmethod
    def _attend(
        self,
        events: Sequence[Event]
    ) -> list[Event]:
        """
        Persist records to disk.

        Must be implemented by subclasses.
        Must not modify `events`.
        """
        raise NotImplementedError


class SessionLogger(BaseLogger):
    def _attend(self, events: list[Event]) -> list[SessionEvent]:
        attended: list[SessionEvent] = []
        for e in events:
            match e.get("type"):
                case "block_start":
                    attended.append(cast(BlockStartEvent, e))
                case "block_abort":
                    attended.append(cast(BlockAbortEvent, e))
                case "block_end":
                    attended.append(cast(BlockEndEvent, e))
                case "trial_start":
                    attended.append(cast(TrialStartEvent, e))
                case "trial_abort":
                    attended.append(cast(TrialAbortEvent, e))
                case "trial_end":
                    attended.append(cast(TrialEndEvent, e))

        return attended


class MouseClickLogger(BaseLogger):
    def __init__(self, *, path: Path, task_code: str):
        super().__init__(path)
        self.task_code = task_code

    def _attend(self, events: list[Event]) -> list[MouseClickEvent]:
        attended: list[MouseClickEvent] = []
        for e in events:
            if (
                e.get("type") == "mouse_click" and
                e.get("task") == self.task_code
            ):
                attended.append(cast(MouseClickEvent, e))

        return attended


class MousePositionLogger(BaseLogger):
    def __init__(self, *, path: Path, task_code: str):
        super().__init__(path)
        self.task_code = task_code

    def _attend(self, events: list[Event]) -> list[MousePositionEvent]:
        attended: list[MousePositionEvent] = []
        for e in events:
            if (
                e.get("type") == "mouse_position" and
                e.get("task") == self.task_code
            ):
                attended.append(cast(MousePositionEvent, e))

        return attended

