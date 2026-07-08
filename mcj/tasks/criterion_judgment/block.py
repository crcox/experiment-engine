from typing import Sequence
from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.emitters import (
    emit_block_execution_start, emit_block_execution_end,
    emit_block_preamble_start,    emit_block_preamble_end,
    emit_block_trials_start,    emit_block_trials_end,
)
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.environments import Environment
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.execution import ExecutionContext
from mcj.runtime.synchronization import wait_for_block_start

from mcj.plans.criterion_judgment.schema import CriterionJudgmentBlockPlan, CriterionJudgmentPlan
from mcj.tasks.criterion_judgment.emitters import emit_condition_set
from mcj.tasks.criterion_judgment.timing import PreambleTiming, TrialTiming, build_schedule

from mcj.tasks.criterion_judgment.prompt import present_prompt
from mcj.tasks.criterion_judgment.definition import present_definition
from mcj.tasks.criterion_judgment.trial import run_trial
from mcj.tasks.criterion_judgment.actions import CJAction

def execute_block(factory: StimFactory, *,
        block_index: int,
        run_ctx: ExecutionContext[CJAction]
) -> None:
    session = run_ctx.session
    ctx = session.ctx
    profile_cfg = run_ctx.profile_cfg
    session_plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)

    emit_block_execution_start(ctx, block_index)
    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        # --- Hooks ---
        print("[DEBUG] session.on_block_start", session.on_block_start)
        if session.on_block_start is not None:
            for hook in session.on_block_start:
                hook()

        # --- Wait for signal to begin the block ---
        if session.environment == Environment.SCANNER:
            t0 = wait_for_block_start(session)
        else:
            t0 = session.ctx.now()
        
        # --- Build or select block configuration ---
        block_plan = session_plan.blocks[block_index]
        block_schedule = build_schedule(t0, block_plan.ntrials, profile_cfg)
        emit_condition_set(ctx, condition=block_plan.condition)

        # --- Run block preamble ---
        run_block_preamble(
            factory,
            block_index=block_index,
            block_plan=block_plan,
            run_ctx=run_ctx,
            timing=block_schedule.preamble,
        )

        # --- Run block trials ---
        run_block_trials(
            factory,
            block_index=block_index,
            block_plan=block_plan,
            run_ctx=run_ctx,
            timing=block_schedule.trials,
        )

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__ 
        raise

    finally:
        if session.on_block_end is not None:
            for hook in session.on_block_end:
                hook()

        emit_block_execution_end(ctx, index=block_index, reason=end_reason, cause=end_cause)

def run_block_preamble(
        factory: StimFactory,
        *,
        block_index: int,
        block_plan: CriterionJudgmentBlockPlan,
        run_ctx: ExecutionContext[CJAction],
        timing: PreambleTiming | None
    ):

    session = run_ctx.session
    environment = session.environment
    ctx = session.ctx

    emit_block_preamble_start(ctx, block_index)
    end_reason = EndReason.COMPLETE
    end_cause = None

    if timing is not None:
        prompt_off = timing.prompt_off
        definition_off = timing.definition_off
    else:
        prompt_off = None
        definition_off = None

    try:
        present_prompt(
            factory,
            block_index=block_index,
            run_ctx=run_ctx,
            end_time=prompt_off ,
        )

        if environment.allows_definition and block_plan.condition.requires_definition:
            present_definition(
                factory,
                block_index,
                end_time=definition_off,
                run_ctx=run_ctx
            )

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__ 
        raise

    finally:
        emit_block_preamble_end(ctx, index=block_index, reason=end_reason, cause=end_cause)


def run_block_trials(
        factory: StimFactory,
        *,
        block_index: int,
        block_plan: CriterionJudgmentBlockPlan,
        run_ctx: ExecutionContext[CJAction],
        timing: Sequence[TrialTiming] | None
    ):
    session = run_ctx.session
    ctx = session.ctx

    emit_block_trials_start(ctx, block_index)
    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        for trial_index, trial in enumerate(block_plan.trials):
            if timing is not None:
                trial_timing = timing[trial_index]
            else:
                trial_timing = None

            run_trial(
                factory,
                trial,
                block_index=block_index,
                trial_index=trial_index,
                trial_timing=trial_timing,
                run_ctx=run_ctx,
            )

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__ 
        raise

    finally:
        emit_block_trials_end(ctx, index=block_index, reason=end_reason, cause=end_cause)


def run_block(factory: StimFactory, *,
        block_index: int,
        run_ctx: ExecutionContext[CJAction]
) -> None:
    session = run_ctx.session
    ctx = session.ctx
    profile_cfg = run_ctx.profile_cfg
    session_plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)

    # --- Hooks ---
    if session.on_block_start is not None:
        for hook in session.on_block_start:
            hook()

    # --- Wait for signal to begin the block ---
    if session.environment == Environment.SCANNER:
        alignment = wait_for_block_start(session)
        t0 = alignment.t0_system_s
    else:
        t0 = session.ctx.now()

    # --- Build or select block configuration ---
    block_plan = session_plan.blocks[block_index]
    environment = session.environment
    trial_timing = build_schedule(t0, block_plan.ntrials, profile_cfg)

    # --- Start block ---
    emit_block_trials_start(ctx, block_index)
    emit_condition_set(ctx, condition=block_plan.condition)

    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        present_prompt(
            factory,
            block_index=block_index,
            run_ctx=run_ctx,
            end_time=trial_timing[0].fixation_on
        )

        if environment.allows_definition and block_plan.condition.requires_definition:
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
        if session.on_block_end is not None:
            for hook in session.on_block_end:
                hook()

        emit_block_end(ctx, index=block_index, reason=end_reason, cause=end_cause)

