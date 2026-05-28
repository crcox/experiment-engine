from __future__ import annotations

from enum import Enum, auto
from psychopy.visual.window import Window
from psychopy.hardware.keyboard import Keyboard
from mcj.stimuli.schema import StimulusPool
from mcj.plans.criterion_judgment.schema import CriterionJudgmentPlan
from mcj.runtime.modes import TrialModeConfig
from mcj.runtime.visuals import SequenceMTSVisuals
from mcj.runtime.time import Timer
from mcj.runtime.context import SessionContext
from mcj.runtime.exceptions import EscapePressed
from mcj.runtime.end_reasons import (
    TRIAL_ERROR, TRIAL_ABORTED, TRIAL_COMPLETE, TRIAL_TIMEOUT,
    BLOCK_ERROR, BLOCK_ABORTED, BLOCK_COMPLETE,
)
from mcj.routines.criterion_judgment.emitters import(
    emit_block_start, emit_block_end,
    emit_trial_start, emit_trial_end
)

class TrialState(Enum):
    AWAITING_RESPONSE = auto()
    FEEDBACK = auto()
    DONE = auto()


# ---- Routines are defined beyond this point ----
def run_block(win: Window, *,
        block_index: int,
        stimuli: StimulusPool,
        visuals: SequenceMTSVisuals,
        ring_positions: list[tuple[float, float]],
        start_at: int,
        ctx: SessionContext,
        mode: TrialModeConfig,
        keyboard: Keyboard | None = None,
) -> int:
    plan: CriterionJudgmentPlan = ctx.get_plan("criterion_judgment", role="practice")
    trial_plan = plan.trial_plan
    block_plan = plan.blocks[block_index]
    if mode.provide_feedback:
        block_plan = ctx.practice_plan.blocks[block_index]
        trial_plan = ctx.practice_plan.trial_plan
    else:
        block_plan = ctx.plan.blocks[block_index]
        trial_plan = ctx.plan.trial_plan

    emit_block_start(ctx, mode, block_index)

    for image_id, pos in zip(block_plan.image_by_ring_slot, ring_positions):
        stim = stimuli['ring'][image_id]
        stim.pos = pos

    block_timer = Timer(ctx.clock)
    node_index=start_at
    try:
        while True:
            target_node = trial_plan['node_sequence'][node_index]
            target_image = trial_plan['image_by_node'][target_node]

            _run_trial(win, block_index, node_index, target_image, stimuli, visuals, ctx, mode, mouse_tracker, keyboard)
            node_index += 1

            if node_index >= len(trial_plan['node_sequence']):
                block_end_reason = BLOCK_COMPLETE
                block_end_cause = None
                break

            block_timeout = (
                mode.block_duration_seconds and
                block_timer.elapsed() > mode.block_duration_seconds
            )
            if block_timeout:
                block_end_reason = BLOCK_COMPLETE
                block_end_cause = None
                break

    except EscapePressed as e:
        block_end_reason = BLOCK_ABORTED
        block_end_cause = "escape_key"
        raise

    except Exception as e:
        block_end_reason = BLOCK_ERROR
        block_end_cause = type(e).__name__ 
        raise

    finally:
        emit_block_end(ctx, mode, block_index, block_end_reason, block_end_cause)

    return node_index


def _run_trial(win: Window, block_index: int, node_index: int, target: str,
               stimuli: StimulusPool, visuals: SequenceMTSVisuals,
               ctx: SessionContext, mode: TrialModeConfig,
               mouse_tracker: MouseTracker, keyboard: Keyboard | None = None) -> None:

    center_stim = stimuli['center'][target]
    target_stim = stimuli['ring'][target]
    trial_timer = Timer(ctx.clock)

    highlight = visuals.highlight
    highlight.pos = target_stim.pos
    highlight.size = target_stim.size

    emit_trial_start(ctx, mode, block_index, node_index, target)

    state = TrialState.AWAITING_RESPONSE
    try:
        while state is not TrialState.DONE:
            for ring_stim in stimuli['ring'].values():
                ring_stim.draw()

            center_stim.draw()
            win.flip()

            mouse_state = mouse_tracker.poll()

            if mouse_state:
                emit_mouse_clicks(ctx, mode, mouse_state, block_index, node_index, target_stim)
                emit_mouse_position(ctx, mode, mouse_state, block_index, node_index)

            if state is TrialState.AWAITING_RESPONSE:
                target_was_clicked = (
                    mouse_state and
                    mouse_state.changed.left and
                    mouse_state.pressed.left and
                    target_stim.contains(mouse_state.position)
                )
                if target_was_clicked:
                    trial_end_reason = TRIAL_COMPLETE
                    trial_end_cause = None
                    if mode.provide_feedback:
                        state = TrialState.FEEDBACK
                        feedback_timer = Timer(ctx.clock)
                    else:
                        state = TrialState.DONE

                timeout = (
                    mode.trial_duration_seconds and
                    trial_timer.elapsed() > mode.trial_duration_seconds
                )
                if timeout:
                    trial_end_reason = TRIAL_TIMEOUT
                    trial_end_cause = None
                    if mode.provide_feedback:
                        state = TrialState.FEEDBACK
                        feedback_timer = Timer(ctx.clock)
                    else:
                        state = TrialState.DONE

            if state is TrialState.FEEDBACK and (fb := mode.feedback):
                highlight.lineColor = (
                    fb.color_positive
                    if trial_end_reason == TRIAL_COMPLETE
                    else fb.color_negative
                )
                highlight.draw()

                feedback_timeout = (
                    fb.duration_seconds and
                    feedback_timer.elapsed() >= fb.duration_seconds
                )

                if feedback_timeout:
                    state = TrialState.DONE

            # --- Check if the escape key has been pressed ---
            escape_key_pressed = (
                keyboard and
                keyboard.getKeys(["escape"], waitRelease=False)
            )
            if escape_key_pressed:
                trial_end_reason = TRIAL_ABORTED
                raise EscapePressed


    except EscapePressed as e:
        trial_end_reason = TRIAL_ABORTED
        trial_end_cause = "escape_key"
        raise

    except Exception as e:
        trial_end_reason = TRIAL_ERROR
        trial_end_cause = type(e).__name__
        raise

    finally:
        emit_trial_end(
            ctx,
            mode=mode,
            block_index=block_index,
            node_index=node_index,
            reason=trial_end_reason,
            cause=trial_end_cause
        )
        target_stim.setBorderColor(None)

