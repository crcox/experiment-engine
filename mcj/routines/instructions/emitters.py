from mcj.runtime.emitter_factory import make_emitter

# Bounded Events ----
emit_instruction_start = make_emitter("instruction_start")
emit_instruction_end = make_emitter("instruction_end", has_reason=True)
emit_slide_start = make_emitter("slide_start")
emit_slide_end = make_emitter("slide_end", has_reason=False)
