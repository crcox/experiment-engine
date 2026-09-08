# --- Standard library ---
import json
from pathlib import Path
from platform import python_version

from mcj.config.experiment import EXPERIMENT_NAME

# --- Config ---
from mcj.config.paths import paths
from mcj.dev.session_info import StaticSessionInfoProvider

# --- Runtime core ---
from mcj.reporting.criterion_judgment.report import build_trial_csv

# --- Routines ---
from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.backend import RenderBackend
from mcj.runtime.emitters import (
    emit_environment_set,
    emit_profile_set,
    emit_session_end,
    emit_session_start,
)
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import ExperimentAbort, ScriptNotExhaustedError
from mcj.runtime.execution import ExecutionContext
from mcj.runtime.setup import build_session, resolve_display
from mcj.tasks.criterion_judgment import task as cj_task
from mcj.tasks.criterion_judgment.actions import CJAction

# --- Task Runtime and Configuration ---
from mcj.tasks.criterion_judgment.display import (
    CJDefinitionDisplay,
    CJPromptDisplay,
)

# --- UI / components ---
from mcj.ui.dialogs import PsychoPyDialogProvider

CriterionJudgmentDisplay = CJPromptDisplay | CJDefinitionDisplay

DEV_ENVIRONMENT = True
RENDER_BACKEND = RenderBackend.PSYCHOPY

if DEV_ENVIRONMENT or RENDER_BACKEND == RenderBackend.FAKE:
    # from mcj.dev.scripts import test_experiment_scanner_script

    provider = StaticSessionInfoProvider(
        {
            "task": "criterion_judgment",
            "environment": "local",
            "profile": "test_experiment",
            "input_mode": "real",
            # "script": test_experiment_scanner_script(),
            # "enable_triggers": True,
        }
    )
else:
    provider = PsychoPyDialogProvider()


def run():
    # --- Collect and then set session_info ---
    session_info = provider.get_session_info(EXPERIMENT_NAME)

    paths.initialize(
        root=Path.cwd(),
    )

    session, profile_bundle, session_logger = build_session(
        session_info, backend=RENDER_BACKEND
    )

    factory, display = resolve_display(
        session_info, backend=RENDER_BACKEND, dev_environment=DEV_ENVIRONMENT
    )

    # --- Write session.json ---
    session.ctx.data_dir.mkdir(parents=True, exist_ok=True)
    with open(session.ctx.data_dir / "session.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "type": "session_start",
                "time": session.ctx.now(),
                "subject_id": session_info.subject_id,
                "profile": session_info.profile.value,
                "environment": session_info.environment.value,
                "input_mode": session_info.input_mode.value,
                "display": display.to_dict(),
                "psychopy_version": factory.version(),
                "python_version": python_version(),
            },
            f,
        )

    # --- Start Session ---
    emit_session_start(session.ctx)
    emit_environment_set(session.ctx, session_info.environment)
    emit_profile_set(session.ctx, session_info.profile)

    end_reason = EndReason.COMPLETE
    end_cause = None

    # =======================================
    # --- BEGIN PRESENTING TO PARTICIPANT ---
    # =======================================
    try:
        # --- Bundle runtime context and configuration ---
        instruction_ctx = ExecutionContext[InstructionAction](
            session=session,
            profile_cfg=profile_bundle["instructions"],
        )

        task_ctx = ExecutionContext[CJAction](
            session=session,
            profile_cfg=profile_bundle["task"],
        )

        cj_task.run_task(
            factory,
            instruction_ctx=instruction_ctx,
            task_ctx=task_ctx,
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
        emit_session_end(session.ctx, reason=end_reason, cause=end_cause)
        session_logger.write_new(session.ctx.recorder)
        build_trial_csv(
            session.ctx.recorder.events(),
            session.ctx.data_dir / "session_trials.csv",
        )
        factory.close()
        if session.scheduler is not None and not session.scheduler.is_finished:
            raise ScriptNotExhaustedError(
                remaining_events=session.scheduler.remaining_events
            )


if __name__ == "__main__":
    run()
