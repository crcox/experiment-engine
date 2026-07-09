from mcj.runtime.emitter_factory import make_emitter
from mcj.routines.instructions.event_types import InstructionsEventType

# Bounded Events ----
emit_instruction_start = make_emitter(InstructionsEventType.INSTRUCTION_START.value)
emit_instruction_end = make_emitter(InstructionsEventType.INSTRUCTION_END.value, has_reason=True)
emit_slide_start = make_emitter(InstructionsEventType.SLIDE_START.value)
emit_slide_end = make_emitter(InstructionsEventType.SLIDE_END.value, has_reason=False)
