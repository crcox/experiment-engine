from mcj.adapters.psychopy.types import KeyPress
from mcj.adapters.psychopy.protocols import KeyboardLike

def get_keypresses(device: KeyboardLike) -> list[KeyPress] | None:
    return device.getKeys(keyList=None, ignoreKeys=None, clear=True, waitRelease=False)
