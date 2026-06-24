from __future__ import annotations

from collections import deque
from dataclasses import replace

from mcj.runtime.time import Clock
from mcj.runtime.input_events import ButtonEvent, ButtonDevice
from mcj.runtime.input import InputAdapter, AdapterType

from mcj.adapters.psychopy.api import get_keypresses
from mcj.adapters.psychopy.protocols import KeyboardLike


class KeyboardAdapter(InputAdapter):
    """
    InputAdapter for PsychoPy keyboard input.

    Only keys specified in `allowed_keys` are emitted as ButtonEvents.
    All other keypresses are ignored at ingestion time.

    Events are assumed to already be in system clock time.
    """
    _clock: Clock
    _event_buffer: deque[ButtonEvent]
    _kb: KeyboardLike
    def __init__(
        self,
        *,
        clock: Clock,
        kb: KeyboardLike | None=None,
    ):
        from psychopy.hardware.keyboard import Keyboard
        if kb is None:
            self._kb = Keyboard(clock=clock)
        else:
            self._kb = kb

        self._event_buffer: deque[ButtonEvent] = deque()


    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.KEYBOARD


    def update(self) -> None:
        """
        Ingest KeyPress events from Keyboard device and stage ButtonEvents in
        the event buffer.
        """
        keys = get_keypresses(self._kb)

        if keys is None:
            return

        for k in keys:
            self._event_buffer.append(ButtonEvent(
                time=k.rt,
                code=k.name,
                device=ButtonDevice.KEYBOARD,
                is_press=True
            ))

    def pop_events(self) -> list[ButtonEvent]:
        """
        Return and clear all currently staged events.
        """
        events = list(self._event_buffer)
        self._event_buffer.clear()
        return events


    def peek_events(self) -> list[ButtonEvent]:
        """
        Return staged events without clearing them.
        """
        events = list(self._event_buffer)
        return events

    def clear(self):
        self._kb.clearEvents()
        self._event_buffer.clear()

    def inject_event(self, event: ButtonEvent) -> None:
        self._event_buffer.append(event)
