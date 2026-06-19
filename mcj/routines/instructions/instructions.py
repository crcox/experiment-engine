from typing import Sequence

from mcj.runtime.execution import ExecutionContext
from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.emitters import emit_button_event, emit_scanner_trigger
from mcj.instructions.schema import InstructionSlide
from mcj.routines.instructions.emitters import (
    emit_instruction_start, emit_instruction_end,
    emit_slide_start, emit_slide_end,
)
from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import EscapePressed
from mcj.runtime.input_events import TriggerEvent, ButtonEvent
from mcj.runtime.states import InstructionState
from mcj.instructions.display import InstructionDisplay


def present_instructions(
        factory: StimFactory,
        slides: Sequence[InstructionSlide],
        run_ctx: ExecutionContext[InstructionAction]
    ):
    session = run_ctx.session
    ctx = session.ctx

    profile_cfg = run_ctx.profile_cfg

    display = InstructionDisplay(factory)
    state = InstructionState.INSTRUCTION
    mapping_factory = profile_cfg.action_mapping_by_state[state]
    mapping = mapping_factory(run_ctx)

    # --- Start Instructions
    index = 0
    emit_instruction_start(ctx)


    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        while index < len(slides):
            slide = slides[index]
            emit_slide_start(ctx)

            ctx.input.update()
            display.update(slide)

            events = ctx.input.pop_events()
            should_advance = False

            for event in events:
                if isinstance(event, TriggerEvent):
                    emit_scanner_trigger(ctx, event)

                if isinstance(event, ButtonEvent):
                    emit_button_event(ctx, event)

                    if event.code == "escape":
                        raise EscapePressed

                    action = mapping.interpret(event)
                    if action == InstructionAction.ADVANCE:
                        should_advance = True
                        break # one transition per frame

                        
            display.draw()
            factory.flip()

            if should_advance:
                emit_slide_end(ctx)
                index += 1


    except EscapePressed as e:
        end_reason = EndReason.ABORTED
        end_cause = "escape_key"
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_instruction_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )


