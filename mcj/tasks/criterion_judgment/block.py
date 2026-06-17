from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.emitters import emit_block_start, emit_block_end
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.context import RuntimeContext
from mcj.runtime.modes import Mode

from mcj.plans.criterion_judgment.schema import CriterionJudgmentPlan
from mcj.tasks.criterion_judgment.emitters import emit_condition_set
from mcj.tasks.criterion_judgment.timing import build_schedule

from mcj.tasks.criterion_judgment.prompt import present_prompt
from mcj.tasks.criterion_judgment.definition import present_definition
from mcj.tasks.criterion_judgment.trial import run_trial

def run_block(factory: StimFactory, *,
        block_index: int,
        t0: float,
        run_ctx: RuntimeContext
) -> None:
    ctx = run_ctx.ctx
    role_cfg = run_ctx.role_cfg
    session_plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)

    # --- Build or select block configuration ---
    block_plan = session_plan.blocks[block_index]
    mode = run_ctx.mode
    trial_timing = build_schedule(t0, block_plan.ntrials, role_cfg)

    # --- Start block ---
    emit_block_start(ctx, block_index)
    emit_condition_set(ctx, condition=block_plan.condition)

    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        if mode == Mode.SCANNER:
            present_prompt(
                factory,
                block_index=block_index,
                run_ctx=run_ctx,
                end_time=trial_timing[0].fixation_on
            )

        if mode == Mode.PRACTICE:
            present_prompt(
                factory,
                block_index=block_index,
                run_ctx=run_ctx,
                end_time=None
            )

            present_definition(factory, block_index, end_time=None, run_ctx=run_ctx)

        for trial_index, trial in enumerate(block_plan.trials):
            run_trial(factory, trial,
                      block_index=block_index,
                      trial_index=trial_index,
                      trial_timing=trial_timing[trial_index],
                      run_ctx=run_ctx)


    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__ 
        raise

    finally:
        emit_block_end(ctx, index=block_index, reason=end_reason, cause=end_cause)

