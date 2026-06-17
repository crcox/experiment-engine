# --- Standard library ---
from pathlib import Path
from platform import python_version
import json


# --- Config ---
from mcj.config.paths import paths
from mcj.config.experiment import EXPERIMENT_NAME


# --- Runtime core ---
from mcj.runtime.backend import RenderBackend
from mcj.runtime.context import RuntimeContext
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.emitters import (
    emit_session_start,
    emit_session_end,
    emit_mode_set,
    emit_role_set,
)
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.roles import PlanRole
from mcj.runtime.setup import build_session, resolve_display

# --- Task Runtime and Configuration ---
from mcj.tasks.criterion_judgment.display import (
    CriterionJudgmentPromptDisplay,
    CriterionJudgmentDefinitionDisplay,
)
from mcj.tasks.criterion_judgment.config import  CriterionJudgmentTaskConfig

# --- UI / components ---
from mcj.ui.dialogs import PsychoPyDialogProvider
from mcj.dev.session_info import StaticSessionInfoProvider

# --- Routines ---
from mcj.tasks.criterion_judgment import task as cj_task

CriterionJudgmentDisplay = CriterionJudgmentPromptDisplay | CriterionJudgmentDefinitionDisplay

DEV_MODE = True
RENDER_BACKEND = RenderBackend.FAKE

if DEV_MODE or RENDER_BACKEND == RenderBackend.FAKE:
    from mcj.dev.scripts import test_practice_script

    provider = StaticSessionInfoProvider({
        "subject_id": 999,
        "mode": "practice",
        "role": "dev",
        "input_backend": "scripted",
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

    ctx, role_cfg, session_logger = build_session(session_info, backend=RENDER_BACKEND)

    print(ctx.input_backend)
    for term in role_cfg.termination_by_state.items():
        print(term)

    factory, display = resolve_display(session_info, backend=RENDER_BACKEND, dev_mode=DEV_MODE)

    # --- Write session.json ---
    paths.DATA.mkdir(parents=True, exist_ok=True)
    with open(paths.DATA / "session.json", 'w', encoding='utf-8') as f: 
        json.dump({
            "type": "session_start",
            "time": ctx.now(),
            "subject_id": session_info.subject_id,
            "role": session_info.role.value,
            "mode": session_info.mode.value,
            "input_backend": session_info.input_backend.value,
            "display": display.to_dict(),
            "psychopy_version": factory.version(),
            "python_version": python_version()
        }, f)

    # --- Start Session ---
    emit_session_start(ctx)
    emit_mode_set(ctx, session_info.mode)
    emit_role_set(ctx, session_info.role)

    end_reason = EndReason.COMPLETE
    end_cause = None

    # =======================================
    # --- BEGIN PRESENTING TO PARTICIPANT ---
    # =======================================
    try:
        # --- Bundle runtime context and configuration ---
        run_ctx=RuntimeContext(ctx=ctx, role_cfg=role_cfg, mode=session_info.mode)

        run_cfg = CriterionJudgmentTaskConfig(
            instructions_path = {
                PlanRole.PRACTICE: paths.INSTRUCTIONS / "practice.yaml",
                PlanRole.MAIN: paths.INSTRUCTIONS / "main.yaml",
                PlanRole.DEV: paths.INSTRUCTIONS / "practice.yaml",
            }[session_info.role]
        )

        cj_task.run(factory, run_ctx=run_ctx, run_cfg=run_cfg)

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_session_end(ctx, reason=end_reason, cause=end_cause)
        session_logger.write_new(ctx.recorder)
        factory.close()


if __name__ == "__main__":
    run()
