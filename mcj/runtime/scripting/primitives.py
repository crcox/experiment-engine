from typing import Callable, Literal

Target = Literal["cedrus", "keyboard"]

from mcj.runtime.scripting.builder import ScriptBuilder

# The following helpers are for use with repeat() and sequence()
def instruction_slide(s: ScriptBuilder, target: Target | None = None):
    return s.press("space", target=target)

def fixation(s: ScriptBuilder, target: Target | None = None):
    return s.press("space", target=target)

def feedback(s: ScriptBuilder, target: Target | None = None):
    return s.press("space", target=target)

def respond_left(s: ScriptBuilder, target: Target | None = None):
    return s.press("f", target=target)

def respond_right(s: ScriptBuilder, target: Target | None = None):
    return s.press("j", target=target)

def respond_left_keyboard(s: ScriptBuilder):
    return s.press("0", target="keyboard")

def respond_right_keyboard(s: ScriptBuilder):
    return s.press("2", target="keyboard")

def respond_left_cedrus(s: ScriptBuilder):
    return s.press("0", target="cedrus")

def respond_right_cedrus(s: ScriptBuilder):
    return s.press("2", target="cedrus")

def send_scanner_trigger(s: ScriptBuilder):
    return s.trigger(4)

def sequence(*fns: Callable[[ScriptBuilder], ScriptBuilder]):
    def apply(s: ScriptBuilder) -> ScriptBuilder:
        for fn in fns:
            fn(s)
        return s
    return apply

