from __future__ import annotations

EventDict = dict[str, object]

SESSION_EVENTS = {
    "session_start",
    "session_end",
    "block_start",
    "block_end",
    "trial_start",
    "trial_end",
    "stimulus_start",
    "stimulus_end",
    "feedback_start",
    "feedback_end",
    "instruction_start",
    "instruction_end",
    "slide_start",
    "slide_end",
    "alignment_start",
    "alignment_end",
    "task_start",
    "task_end",
    "fixation_start",
    "fixation_end",
    "prompt_start",
    "prompt_end",
    "definition_start",
    "definition_end",
    "condition_set",
    "mode_set",
    "role_set",
    "stimulus_onset",
    "response",
    "button_event",
    "scanner_trigger",
}


class EventRecorder:
    """
    Append-only in-memory event stream for a single session.

    Producers emit semantic events.
    Consumers (loggers) read incrementally using cursors.
    """

    def __init__(self) -> None:
        self._events: list[EventDict] = []

    def emit(self, event: EventDict) -> None:
        """
        Record a new event.

        Events must be JSON-serializable dicts.
        """
        self._events.append(event)

    def events(self) -> list[EventDict]:
        """
        Return the full event list.

        Intended for read-only consumption by loggers.
        """
        return self._events
