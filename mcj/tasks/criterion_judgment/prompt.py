from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.context import RuntimeContext
from mcj.runtime.emitters import emit_button_event, emit_scanner_trigger
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.mapping import KeyPressMapping
from mcj.runtime.input_events import TriggerEvent, ButtonEvent
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentResponse as Response
)
from mcj.plans.criterion_judgment.prompts_loader import load_prompt
from mcj.tasks.criterion_judgment.display import CriterionJudgmentPromptDisplay
from mcj.tasks.criterion_judgment.emitters import emit_condition_set, emit_prompt_start, emit_prompt_end
from mcj.runtime.exceptions import EscapePressed
from mcj.runtime.states import PromptState

def present_prompt(
        factory: StimFactory,
        block_index:int,
        end_time: float | None,
        run_ctx: RuntimeContext
    ):
    ctx = run_ctx.ctx
    plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)
    role_cfg = run_ctx.role_cfg

    # --- Build or select prompt configuration ---

    block_plan = plan.blocks[block_index]
    prompt = load_prompt(block_plan.condition)


    display = CriterionJudgmentPromptDisplay(factory)

    state = PromptState.PROMPT
    mapping = KeyPressMapping({"space"})
    termination = role_cfg.termination_by_state[state]
    done = termination.make_done_predicate(
        ctx.now,
        end_time_seconds=end_time,
        response_recorded_ref=lambda: response_recorded
    )

    if plan.left_response == Response.YES:
        left_label, right_label = (Response.YES, Response.NO)
    else:
        left_label, right_label = (Response.NO, Response.YES)

    display.update(
        prompt_frame_text=prompt.prompt_frame,
        prompt_text=prompt.prompt,
        left_text=left_label.value,
        right_text=right_label.value
    )
    draw = display.draw
    
    # --- Start prompt
    emit_condition_set(ctx, condition=block_plan.condition)
    emit_prompt_start(ctx)

    end_reason = EndReason.COMPLETE
    end_cause = None

    response_recorded = False

    try:
        while True:
            ctx.input.update()

            events = ctx.input.pop_events()
            for event in events:
                if isinstance(event, TriggerEvent):
                    emit_scanner_trigger(ctx, event)

                if isinstance(event, ButtonEvent):
                    emit_button_event(ctx, event)

                    if event.code == "escape":
                        raise EscapePressed

                    result = mapping.interpret(event)
                    if result is not None and not response_recorded:
                        response_recorded = True
                        
            draw()
            factory.flip()

            if done():
                break

    except EscapePressed as e:
        end_reason = EndReason.ABORTED
        end_cause = "escape_key"
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_prompt_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )


