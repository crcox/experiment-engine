from mcj.runtime.execution import ExecutionContext
from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.emitters import (
    emit_button_event,
    emit_scanner_trigger,
)
from mcj.runtime.input_events import TriggerEvent, ButtonEvent
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentResponse as Response
)
from mcj.plans.criterion_judgment.prompts_loader import load_prompt
from mcj.tasks.criterion_judgment.display import CriterionJudgmentDefinitionDisplay
from mcj.tasks.criterion_judgment.emitters import (
    emit_condition_set,
    emit_definition_start,
    emit_definition_end,
)
from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.runtime.exceptions import EscapePressed
from mcj.runtime.states import DefinitionState

def present_definition(
        factory: StimFactory,
        block_index:int,
        end_time: float | None,
        run_ctx: ExecutionContext[CJAction]
    ):
    session = run_ctx.session
    ctx = session.ctx
    plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)
    profile_cfg = run_ctx.profile_cfg

    # --- Build or select prompt configuration ---

    block_plan = plan.blocks[block_index]
    prompt = load_prompt(block_plan.condition)

    display = CriterionJudgmentDefinitionDisplay(factory)

    state = DefinitionState.DEFINITION
    mapping_factory = profile_cfg.action_mapping_by_state[state]
    mapping = mapping_factory(run_ctx)
    termination = profile_cfg.termination_by_state[state]
    done = termination.make_done_predicate(
        ctx.now,
        end_time_seconds=end_time,
        action_ref=lambda: last_action
    )

    if plan.left_response == Response.YES:
        left_label, right_label = (Response.YES, Response.NO)
    else:
        left_label, right_label = (Response.NO, Response.YES)

    display.update(
        definition_text=prompt.require_definition(),
        left_text=left_label.value,
        right_text=right_label.value
    )
    draw = display.draw

    # --- Start definition
    emit_condition_set(ctx, condition=block_plan.condition)
    end_reason = EndReason.COMPLETE
    end_cause = None

    state = DefinitionState.DEFINITION
    emit_definition_start(ctx)
    last_action: CJAction | None = None
    try:
        while True:
            session.maybe_step_simulation()
            ctx.input.update()

            events = ctx.input.pop_events()
            for event in events:
                if isinstance(event, TriggerEvent):
                    emit_scanner_trigger(ctx, event)

                if isinstance(event, ButtonEvent):
                    emit_button_event(ctx, event)

                    if event.code == "escape":
                        raise EscapePressed

                    last_action = mapping.interpret(event)
                        
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
        emit_definition_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )


