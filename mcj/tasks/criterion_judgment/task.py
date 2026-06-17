from __future__ import annotations

from mcj.instructions.loader import load_instructions
from mcj.plans.criterion_judgment.schema import CriterionJudgmentPlan
from mcj.runtime.context import RuntimeContext
from mcj.runtime.modes import Mode
from mcj.runtime.tasks import Task
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.synchronization import sync_cedrus_and_experiment_clocks
from mcj.runtime.display_primitives import StimFactory

from mcj.routines.instructions import present_instructions

from mcj.tasks.criterion_judgment.config import CriterionJudgmentTaskConfig
from mcj.tasks.criterion_judgment.emitters import emit_task_start, emit_task_end

from mcj.tasks.criterion_judgment.block import run_block

def run(factory: StimFactory, run_ctx: RuntimeContext, run_cfg: CriterionJudgmentTaskConfig):
    ctx = run_ctx.ctx
    role_cfg = run_ctx.role_cfg
    plan = ctx.get_plan_typed(
        Task.CRITERION_JUDGMENT,
        CriterionJudgmentPlan
    )

    instruction_slides = load_instructions(run_cfg.instructions_path)

    emit_task_start(ctx)
    end_reason = EndReason.COMPLETE
    end_cause = None
    try:
        # --- Present instructions ---
        present_instructions(
            factory,
            slides=instruction_slides,
            run_ctx=run_ctx,
        )
        
        for block_index in range(plan.nblocks):
            if run_ctx.mode == Mode.SCANNER:
                alignment = sync_cedrus_and_experiment_clocks(ctx)
                t0 = alignment.t0_system_s
            else:
                t0 = ctx.now()

            run_block(
                factory,
                block_index=block_index,
                t0=t0,
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
        emit_task_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )


