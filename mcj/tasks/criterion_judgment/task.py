from __future__ import annotations

from mcj.instructions.loader import load_instructions
from mcj.plans.criterion_judgment.schema import CJPlan
from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.execution import ExecutionContext
from mcj.runtime.tasks import Task
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.display_primitives import StimFactory

from mcj.routines.instructions.instructions import present_instructions

from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.tasks.criterion_judgment.emitters import emit_task_start, emit_task_end

from mcj.tasks.criterion_judgment.block import execute_block


def run_task(
    factory: StimFactory,
    instruction_ctx: ExecutionContext[InstructionAction],
    task_ctx: ExecutionContext[CJAction],
):
    session = task_ctx.session
    plan = session.ctx.get_plan_typed(
        Task.CRITERION_JUDGMENT,
        CJPlan
    )

    instruction_slides = load_instructions(session.ctx.assets.profile / "instructions.yaml")

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
            execute_block(
                factory,
                block_index=block_index,
                run_ctx=task_ctx,
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


