from typing import Callable

from mcj.runtime.scripting.builder import ScriptBuilder

# The following helpers are for use with repeat() and sequence()
def fixation(s: ScriptBuilder):
    return s.press("space")

def feedback(s: ScriptBuilder):
    return s.press("space")

def respond_left(s: ScriptBuilder):
    return s.press("f")

def respond_right(s: ScriptBuilder):
    return s.press("j")

def respond_left_cedrus(s: ScriptBuilder):
    return s.press("0")

def respond_right_cedrus(s: ScriptBuilder):
    return s.press("2")

def send_scanner_trigger(s: ScriptBuilder):
    return s.trigger(4)

def sequence(*fns: Callable[[ScriptBuilder], ScriptBuilder]):
    def apply(s: ScriptBuilder) -> ScriptBuilder:
        for fn in fns:
            fn(s)
        return s
    return apply

