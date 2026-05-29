from platform import python_version
from psychopy import visual, core, __version__ as psychopy_version
from psychopy.hardware import keyboard
from psychopy.visual.rect import Rect
from mcj.ui.dialogs import get_session_info
from mcj.components.instructions import InstructionLayout
from mcj.components.fixation import FixationCross
from mcj.runtime.context import SessionContext
from mcj.runtime.events import EventRecorder
from mcj.runtime.exceptions import ExperimentAbort
from mcj.runtime.emitters import emit_session_start, emit_session_end
from mcj.runtime.end_reasons import SESSION_ERROR, SESSION_COMPLETE
from mcj.runtime.modes import Mode, TrialModeConfig, FeedbackConfig
from mcj.runtime.visuals import SequenceMTSVisuals
from mcj.instructions.loader import load_instructions
from mcj.stimuli.loader import load_word_metadata_csv, build_stimulus_pool
from mcj.plans.loader import load_session_plan, load_practice_plan
from mcj.helpers.quit import quit_psychopy
from mcj.config.paths import paths
from mcj.config.experiment import EXPERIMENT_NAME, CONFIG_BY_ROLE
from mcj.io.loggers import (
    MouseClickLogger,
    MousePositionLogger,
    SessionLogger
)
from mcj import routines
from pathlib import Path
import json


def run():

    try:
        # --- Collect and then set session_info ---
        win = visual.Window(size=(800, 600), color='grey', units='height', fullscr=False)
        session_info = get_session_info(EXPERIMENT_NAME)

        paths.initialize(
            root=Path.cwd(),
            subject_id=session_info.subject_id,
            mode=session_info.mode
        )

        ctx = SessionContext(
            plans={ 
                'scanner': load_session_plan(paths.SESSION_PLAN)
            },
            clock=core.Clock(),
            recorder=EventRecorder(),
            context=CONFIG_BY_ROLE[session_info.role]
        )

        emit_session_start(ctx)


        # --- Write session.json ---
        with open(paths.DATA / "session.json", 'w', encoding='utf-8') as f: 
            json.dump({
                "type": "session_start",
                "time": ctx.clock.getTime(),
                "subject_id": session_info.subject_id,
                "condition": session_info.condition,
                "psychopy_version": psychopy_version,
                "python_version": python_version()
            }, f)


        # --- Configure trial modes ---
        PRACTICE = TrialModeConfig(
            name = "practice",
            task_code = "mcj",
            trial_duration_seconds = 3.0,
            block_duration_seconds = None,
            feedback = FeedbackConfig(
                duration_seconds = 0.5,
                color_positive = "green",
                color_negative = "red",
                color_neutral = None
            )
        )

        EXPERIMENTAL = TrialModeConfig(
            name = "experimental",
            task_code = "mcj",
            trial_duration_seconds = 3.0,
            block_duration_seconds = 210.0,
            feedback = None
        )


        # --- Configure routine/task layouts ---
        SEQ_MTS_LAYOUT_CONFIG = mcj.layout.RingLayoutConfig()


        # --- Define I/O devices ---
        kb = keyboard.Keyboard()

        # --- Instantiate loggers ---
        session_logger = SessionLogger(paths.DATA / "session.events.jsonl")

        mcj_click_logger = MouseClickLogger(
            path = paths.DATA / "task-mcj.events.jsonl",
            task_code = "mcj"
        )

        mcj_position_logger = MousePositionLogger(
            path = paths.DATA / "task-mcj.positions.jsonl",
            task_code = "mcj"
        )


        # --- Instantiate shared components and layouts ---
        instruction_layout = InstructionLayout(win)
        fixation = FixationCross(win)


        visuals = SequenceMTSVisuals(
            highlight = Rect(win=win, size=(0.15, 0.15), lineWidth=2)
        )


        # --- Load assets ---
        practice_instructions = load_instructions(
            paths.INSTRUCTIONS / "practice.yaml"
        )

        task_instructions = load_instructions(
            paths.INSTRUCTIONS / "task.yaml"
        )

        end_instructions = load_instructions(
            paths.INSTRUCTIONS / "end.yaml"
        )

        word_table = load_word_metadata_csv()
        stimuli = build_stimulus_pool(win, word_table)


        # --- Run routines ---

        ## Practice Instructions
        routines.practice_instructions.run(
            win,
            layout=instruction_layout,
            slides=practice_instructions["slides"],
            keyboard=kb
        )

        ## mcj (practice mode)
        _ = routines.mcj_task.run_block(
            win,
            start_at=0,
            stimuli=stimuli,
            visuals=visuals,
            block_index=0,
            keyboard=kb,
            ctx=ctx,
            mode=PRACTICE
        )


        ## mcj (experimental mode)
        cursor = 0
        for block_index in range(NUM_BLOCKS):
            cursor = routines.mcj_task.run_block(
                win,
                start_at=cursor,
                stimuli=stimuli,
                visuals=visuals,
                block_index=block_index,
                ring_positions=ring_positions,
                mouse_tracker=mouse_tracker,
                keyboard=kb,
                ctx=ctx,
                mode=EXPERIMENTAL
            )

        # --- Indicate that the session completed successfully ---
        emit_session_end(ctx, reason=SESSION_COMPLETE, cause=None)

    except ExperimentAbort as e:
        emit_session_end(ctx, reason=e.reason, cause=e.cause)

    except Exception as e:
        emit_session_end(ctx, reason=SESSION_ERROR, cause=type(e).__name__)
        raise

    finally:
        session_logger.write_new(ctx.recorder)
        mcj_click_logger.write_new(ctx.recorder)
        mcj_position_logger.write_new(ctx.recorder)
        quit_psychopy(win)

