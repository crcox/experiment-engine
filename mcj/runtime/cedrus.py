import time
from dataclasses import dataclass
from typing import Sequence
from collections import deque

from mcj.adapters.pyxid2.api import get_xid_devices, pop_next_xid_event, XidDeviceLike
from mcj.adapters.pyxid2.types import XidEvent, Stamped, stamp_event
from mcj.runtime.input import InputAdapter, AdapterType
from mcj.runtime.input_events import ButtonEvent, TriggerEvent, ButtonDevice
from mcj.runtime.time import Clock


@dataclass(frozen=True)
class Alignment:
    """
    Mapping between Cedrus device clock (ms) and system clock (seconds).

    t0_device_ms : device timestamp at alignment trigger
    t0_system_s  : system time estimate (midpoint bracket)
    """
    t0_device_ms: float
    t0_system_s: float

class CedrusAdapter(InputAdapter):
    """
    InputAdapter for Cedrus XID devices.

    Responsibilities:
    - Ingest raw XidEvents from device
    - Stamp events with system time
    - Perform clock alignment on first scanner trigger
    - Convert aligned events into ButtonEvent / TriggerEvent

    Invariant:
    - Only aligned events are emitted
    - Unaligned events are dropped (optionally logged in debug environment)
    """
    _clock: Clock
    _dev: XidDeviceLike
    _trigger_key: int
    _event_buffer: deque[TriggerEvent | ButtonEvent]
    _debug: bool

    _last_t_before: float | None
    _align: Alignment | None

    def __init__(
        self,
        *,
        clock: Clock,
        device: XidDeviceLike | None=None,
        device_index: int = 0,
        trigger_key: int = 4,
        debug: bool = False
    ):
        # --- Device selection ---
        if device is not None:
            self._dev = device
        else:
            from pyxid2.pyxid_impl import XidDevice
            attempt = 0
            devices: Sequence[XidDevice] = []
            while not devices and attempt < 10:
                attempt += 1

                if debug:
                    print(f"[DEBUG] get_xid_devices() (Attempt: {attempt})")

                devices = get_xid_devices()
                time.sleep(.01)

            if not devices:
                raise RuntimeError("No Cedrus devices found")

            self._dev = devices[device_index]

        # --- Core state ---
        self._clock = clock
        self._align = None
        self._last_t_before = None

        self._trigger_key = trigger_key
        self._event_buffer: deque[TriggerEvent | ButtonEvent] = deque()

        self._debug = debug


    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.CEDRUS


    # --- Public API ---
    def update(self) -> None:
        """
        Ingest events from Cedrus device, perform alignment if needed,
        and stage aligned events for consumption.
        """
        t_before = self._last_t_before
        self._last_t_before = None

        self._dev.poll_for_response()

        while self._dev.response_queue_size():
            xid_event = pop_next_xid_event(self._dev)

            if xid_event is not None:
                stamped = stamp_event(xid_event, self._clock)

                self._maybe_align(stamped, t_before)

                if self._align is not None:
                    typed_event = self._convert_event(stamped)
                    self._event_buffer.append(typed_event)
                else:
                    self._handle_unaligned_event(stamped)

            self._dev.poll_for_response()


    def pop_events(self) -> list[TriggerEvent | ButtonEvent]:
        """
        Return and clear all currently staged events.
        """
        events = list(self._event_buffer)
        self._event_buffer.clear()
        return events


    def peek_events(self) -> list[TriggerEvent | ButtonEvent]:
        """
        Return staged events without clearing them.
        """
        events = list(self._event_buffer)
        return events


    def clear(self) -> None:
        """
        Drain all pending events from the device and discard them.

        Used before alignment to guarantee that no stale device events
        contaminate the new timebase.
        """
        self._dev.poll_for_response()

        while self._dev.response_queue_size():
            xid_event = pop_next_xid_event(self._dev)

            if xid_event is not None:
                stamped = stamp_event(xid_event, self._clock)
                self._handle_unaligned_event(stamped)

            self._dev.poll_for_response()

        self._event_buffer.clear()

    # --- Alignment API ---
    @property
    def is_aligned(self) -> bool:
        """
        True once a scanner trigger has established clock alignment
        """
        return self._align is not None


    def require_alignment(self) -> Alignment:
        """
        Return alignment, or raise if alignment has not occured.
        """
        if self._align is None:
            raise RuntimeError("Cedrus adapter must be aligned before times can be converted")
        else:
            return self._align


    def set_last_t_before(self, t: float):
        """
        Record system time immediately before calling update().

        This value forms the lower bound of the alignment bracket.
        """
        if self._last_t_before is not None:
            raise RuntimeError(
                "set_last_t_before called twice without update()"
            )
        self._last_t_before = t


    def reset_alignment(self):
        """
        Clear alignment state.

        Should be called after resetting the device clock.
        """
        self._align = None
        self._last_t_before = None


    def reset_device_timer(self):
        """
        Reset Cedrus device timer (XID clock).
        """
        self._dev.reset_timer()


    # --- Private helpers ---
    def _maybe_align(self, stamped: Stamped[XidEvent], t_before: float | None) -> None:
        """
        Attempt alignment using the first observed scanner trigger.

        Uses midpoint bracketing:
            t_system ≈ (t_before + t_after) / 2
        """
        if self._align is not None:
            return

        if t_before is None:
            return

        evt = stamped.payload

        if evt["key"] == self._trigger_key and evt["pressed"]:
            t_device = evt["time"]
            t_after = stamped.system_time
            t_system = (t_before + t_after) / 2.0

            self._set_alignment(Alignment(
                t0_device_ms=t_device,
                t0_system_s=t_system
            ))


    def _set_alignment(self, alignment: Alignment):
        """
        Set alignment once; ignore subsequent attempts.
        """
        if self._align is not None:
            return
        self._align = alignment


    def _handle_unaligned_event(self, stamped: Stamped[XidEvent]) -> None:
        """
        Debug hook for observing dropped events prior to alignment.
        """
        if not self._debug:
            return

        xid_event = stamped.payload

        print(
            "[DEBUG] Dropping unaligned Cedrus event:", xid_event, f"at system_time_s={stamped.system_time:.003f}" 
        )


    def _convert_event(self, stamped: Stamped[XidEvent]) -> TriggerEvent | ButtonEvent:
        """
        Convert a stamped XidEvent into a domain event.
        """
        evt = stamped.payload
        key = evt["key"]
        is_press = evt["pressed"]
        time = self._convert_time(evt["time"])

        if key == self._trigger_key:
            return TriggerEvent(
                time=time,
                device=ButtonDevice.CEDRUS,
                is_press=is_press,
                device_time_ms=evt["time"],
                system_time_s=stamped.system_time,
            )

        return ButtonEvent(
            time=time,
            device=ButtonDevice.CEDRUS,
            code=str(key),
            is_press=is_press,
            device_time_ms=evt["time"],
            system_time_s=stamped.system_time,
        )


    def _convert_time(self, device_time_ms: int) -> float:
        """
        Convert Cedrus device time (ms) to aligned system time (seconds).
        """
        alignment = self.require_alignment()
        delta_ms = device_time_ms - alignment.t0_device_ms
        delta_s = delta_ms / 1000.0

        return alignment.t0_system_s + delta_s

