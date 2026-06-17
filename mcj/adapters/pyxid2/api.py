from __future__ import annotations
from typing import Any, Sequence, TYPE_CHECKING

from mcj.adapters.pyxid2.types import XidEvent, XidDeviceLike

if TYPE_CHECKING:
    from pyxid2.pyxid_impl import XidDevice

def get_xid_devices() -> Sequence["XidDevice"]:
    import pyxid2
    devices = pyxid2.get_xid_devices()

    return devices

def _coerce_event(obj: Any) -> XidEvent:
    if not isinstance(obj, dict):
        raise TypeError(f"Unexpected response time: {type(obj)}")
    required_keys = {"port", "key", "pressed", "time"}
    missing = required_keys - obj.keys()
    if missing:
        raise RuntimeError(
            "XidEvent requires the following missing keys:\n"
            + '\n  '.join(str(m) for m in missing)
        )

    return {
        "port": int(obj["port"]),
        "key": int(obj["key"]),
        "pressed": bool(obj["pressed"]),
        "time": int(obj["time"]),
    }

def pop_next_xid_event(device: XidDeviceLike) -> XidEvent | None:
    response = device.get_next_response()
    return _coerce_event(response)


def update_response_queue(device: "XidDevice") -> None:
    """ Retrieves one event from the remote device queue and appends it to
    device.response_queue """
    device.poll_for_response()

