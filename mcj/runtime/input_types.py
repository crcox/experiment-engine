from collections.abc import Callable

from mcj.runtime.input import InputAdapter
from mcj.runtime.time import Clock

AdapterFactory = Callable[[Clock], InputAdapter]
