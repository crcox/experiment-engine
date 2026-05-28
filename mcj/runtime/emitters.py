from __future__ import annotations
# ---- Define emitter functions ----
# Emitters write important experiment events to a single stream. These are
# later logged at convenient times.
#
# Every emitted event dictionary must have "type" and "time" fields. In all cases,
# except when emitting mouse clicks, time comes from the single, authoratative
# SessionContext.clock, and this is referenced here with ctx.now().
# 
# This is a strict convention. The recorder will not REJECT an event that does
# not define type and time, so it is up to you to maintain the convention.
#
# This flexibility when writing to the event record means that you can store
# whatever information you like in an event. As a guiding principle, the record
# encodes the true facts about what and when important events happed over the
# course of the experiment. Derivatives, like accuracy and response time, will
# be computed all at once when the experiment ends.
#
# It will make your life easier when parsing the event record if each event is
# a flat structure. Avoid nesting lists and dictionaries within event fields
# unless it is absolutely necessary.
from psychopy.visual.image import ImageStim
from mcj.runtime.modes import TrialModeConfig
from mcj.runtime.context import SessionContext
from mcj.runtime.end_reasons import TrialEndReason, BlockEndReason

from mcj.runtime.context import SessionContext
from mcj.runtime.end_reasons import SessionEndReason

def emit_block_start(
        ctx: SessionContext,
        mode: TrialModeConfig,
        block_index: int
    ) -> None:
    ctx.recorder.emit({
        "type": "block_start",
        "time": ctx.now(),
        "task_code": mode.task_code,
        "mode": mode.name,
        "block_index": block_index
    })


def emit_session_start(
        ctx: SessionContext,
    ) -> None:
    ctx.recorder.emit({
        "type": "session_start",
        "time": ctx.now()
    })

def emit_session_end(
        ctx: SessionContext,
        reason: SessionEndReason,
        cause: str | None
    ) -> None:
    ctx.recorder.emit({
        "type": "session_end",
        "time": ctx.now(),
        "reason": reason,
        "cause": cause
    })


def emit_block_end(
        ctx: SessionContext,
        mode: TrialModeConfig,
        block_index: int,
        reason: BlockEndReason,
        cause: str | None
    ) -> None:
    ctx.recorder.emit({
        "type": "block_end",
        "time": ctx.now(),
        "task_code": mode.task_code,
        "mode": mode.name,
        "block_index": block_index,
        "reason": reason,
        "cause": cause
    })

def emit_trial_start(
        ctx: SessionContext,
        mode: TrialModeConfig,
        block_index: int,
        node_index: int,
        target
    ) -> None:
    ctx.recorder.emit({
        "type": "trial_start",
        "time": ctx.now(),
        "task_code": mode.task_code,
        "mode": mode.name,
        "block_index": block_index,
        "node_index": node_index,
        "target": target,
    })

def emit_trial_end(
        ctx: SessionContext,
        mode: TrialModeConfig,
        block_index: int,
        node_index: int,
        reason: TrialEndReason,
        cause: str | None
    ) -> None:
    ctx.recorder.emit({
        "type": "trial_end",
        "time": ctx.now(),
        "task_code": mode.task_code,
        "mode": mode.name,
        "block_index": block_index,
        "node_index": node_index,
        "reason": reason,
        "cause": cause
    })

def emit_mouse_position(
        ctx: SessionContext,
        mode: TrialModeConfig,
        mouse_state: MouseState,
        block_index: int,
        node_index: int
    ) -> None:
    ctx.recorder.emit({
        "type": "mouse_position",
        "time": ctx.now(),
        "task_code": mode.task_code,
        "mode": mode.name,
        "block_index": block_index,
        "node_index": node_index,
        "sample_reason": "periodic",
        "x": mouse_state.position.x,
        "y": mouse_state.position.y
    })

def emit_mouse_clicks(
        ctx: SessionContext,
        mode: TrialModeConfig,
        mouse_state: MouseState,
        block_index: int,
        node_index: int,
        target_stim: ImageStim
    ) -> None:
    for name, is_pressed, is_changed, time, pos in mouse_state.iter_buttons():
        if is_pressed and is_changed:
            ctx.recorder.emit({
                "type": "mouse_click",
                "time": time,
                "task_code": mode.task_code,
                "mode": mode.name,
                "block_index": block_index,
                "node_index": node_index,
                "button": name,
                "x": pos.x,
                "y": pos.y,
                "target": target_stim.name,
                "target_pos": tuple(target_stim.pos),
                "target_size": tuple(target_stim.size),
                "target_contains_click": target_stim.contains(pos),
            })

