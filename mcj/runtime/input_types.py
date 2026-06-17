from typing import Callable

from mcj.runtime.time import Clock
from mcj.runtime.session_info import SessionInfo
from mcj.runtime.input import InputAdapter

AdapterFactory = Callable[[Clock, SessionInfo], InputAdapter]
