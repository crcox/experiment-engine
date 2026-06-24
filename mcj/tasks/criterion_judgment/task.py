from __future__ import annotations

from mcj.instructions.loader import load_instructions
from mcj.plans.criterion_judgment.schema import CriterionJudgmentPlan
from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.execution import ExecutionContext
from mcj.runtime.environments import Environment
from mcj.runtime.tasks import Task
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.synchronization import sync_cedrus_and_experiment_clocks
from mcj.runtime.display_primitives import StimFactory

from mcj.routines.instructions.instructions import present_instructions

from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.tasks.criterion_judgment.config import CriterionJudgmentTaskConfig
from mcj.tasks.criterion_judgment.emitters import emit_task_start, emit_task_end

from mcj.tasks.criterion_judgment.block import run_block


def run(
    factory: StimFactory,
    instruction_ctx: ExecutionContext[InstructionAction],
    task_ctx: ExecutionContext[CJAction],
    run_cfg: CriterionJudgmentTaskConfig
):
    session = task_ctx.session
    plan = session.ctx.get_plan_typed(
        Task.CRITERION_JUDGMENT,
        CriterionJudgmentPlan
    )

    instruction_slides = load_instructions(run_cfg.instructions_path)

    emit_task_start(session.ctx)
    end_reason = EndReason.COMPLETE
    end_cause = None
    try:
        # --- Present instructions ---
        present_instructions(
            factory,
            slides=instruction_slides,
            run_ctx=instruction_ctx,
        )
        
        for block_index in range(plan.nblocks):
            if session.environment == Environment.SCANNER:
                alignment = sync_cedrus_and_experiment_clocks(session)
                t0 = alignment.t0_system_s
            else:
                t0 = session.ctx.now()

            run_block(
                factory,
                block_index=block_index,
                t0=t0,
                run_ctx=task_ctx
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
            session.ctx,
            reason=end_reason,
            cause=end_cause
        )


