# --- Standard library ---
from pathlib import Path
from platform import python_version
import json


# --- Config ---
from mcj.config.paths import paths
from mcj.config.experiment import EXPERIMENT_NAME


# --- Runtime core ---
from mcj.runtime.backend import RenderBackend
from mcj.runtime.execution import ExecutionContext
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.emitters import (
    emit_session_start,
    emit_session_end,
    emit_environment_set,
    emit_profile_set,
)
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.profiles import TaskProfile
from mcj.runtime.setup import build_session, resolve_display

# --- Task Runtime and Configuration ---
from mcj.tasks.criterion_judgment.display import (
    CriterionJudgmentPromptDisplay,
    CriterionJudgmentDefinitionDisplay,
)
from mcj.tasks.criterion_judgment.config import  CriterionJudgmentTaskConfig
from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.tasks.criterion_judgment import task as cj_task

# --- UI / components ---
from mcj.ui.dialogs import PsychoPyDialogProvider
from mcj.dev.session_info import StaticSessionInfoProvider

# --- Routines ---
from mcj.routines.instructions.actions import InstructionAction

CriterionJudgmentDisplay = CriterionJudgmentPromptDisplay | CriterionJudgmentDefinitionDisplay

DEV_ENVIRONMENT = True
RENDER_BACKEND = RenderBackend.FAKE

if DEV_ENVIRONMENT or RENDER_BACKEND == RenderBackend.FAKE:
    from mcj.dev.scripts import test_practice_script

    provider = StaticSessionInfoProvider({
        "subject_id": 999,
        "environment": "local",
        "profile": "dev",
        "input_backend": "simulated",
        "script": test_practice_script()
    })
else:
    provider = PsychoPyDialogProvider()


def run():
    # --- Collect and then set session_info ---
    session_info = provider.get_session_info(EXPERIMENT_NAME)

    paths.initialize(
        root=Path.cwd(),
        subject_id=session_info.subject_id,
    )

    session, profile_bundle, session_logger = build_session(session_info, backend=RENDER_BACKEND)

    factory, display = resolve_display(session_info, backend=RENDER_BACKEND, dev_environment=DEV_ENVIRONMENT)

    # --- Write session.json ---
    paths.DATA.mkdir(parents=True, exist_ok=True)
    with open(paths.DATA / "session.json", 'w', encoding='utf-8') as f: 
        json.dump({
            "type": "session_start",
            "time": session.ctx.now(),
            "subject_id": session_info.subject_id,
            "profile": session_info.task_profile.value,
            "environment": session_info.environment.value,
            "input_backend": session_info.input_backend.value,
            "display": display.to_dict(),
            "psychopy_version": factory.version(),
            "python_version": python_version()
        }, f)

    # --- Start Session ---
    emit_session_start(session.ctx)
    emit_environment_set(session.ctx, session_info.environment)
    emit_profile_set(session.ctx, session_info.task_profile)

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

        run_cfg = CriterionJudgmentTaskConfig(
            instructions_path = {
                TaskProfile.PRACTICE: paths.INSTRUCTIONS / "practice.yaml",
                TaskProfile.MAIN: paths.INSTRUCTIONS / "main.yaml",
                TaskProfile.DEV: paths.INSTRUCTIONS / "practice.yaml",
            }[session_info.task_profile]
        )

        cj_task.run(
            factory,
            instruction_ctx=instruction_ctx,
            task_ctx=task_ctx,
            run_cfg=run_cfg,
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
        factory.close()


if __name__ == "__main__":
    run()
