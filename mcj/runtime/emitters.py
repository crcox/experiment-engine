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
from mcj.runtime.environments import Environment
from mcj.runtime.profiles import ExperimentProfile
from mcj.runtime.input_events import ButtonEvent, TriggerEvent
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.session_context import SessionContext
from mcj.runtime.emitter_factory import make_emitter, make_indexed_emitter


# Mechanical Emitters ----
def emit_button_event(
        ctx: SessionContext,
        btn: ButtonEvent
    ) -> None:
    ctx.recorder.emit({
        "type": "button_event",
        "time": btn.time,
        "code": btn.code,
        "device": btn.device.value,
        "is_press": btn.is_press
    })

def emit_scanner_trigger(
        ctx: SessionContext,
        trigger: TriggerEvent
    ) -> None:
    ctx.recorder.emit({
        "type": "scanner_trigger",
        "time": trigger.time,
        "device": trigger.device.value,
        "is_press": trigger.is_press
    })

# State emitters ----
def emit_environment_set(
    ctx: SessionContext,
    environment: Environment
):
    ctx.recorder.emit({
        "type": "environment_set",
        "environment": environment.value,
        "time": ctx.now()
    })

def emit_profile_set(
    ctx: SessionContext,
    profile: ExperimentProfile
):
    ctx.recorder.emit({
        "type": "profile_set",
        "profile": profile.value,
        "time": ctx.now()
    })


# Structural emitters ----
emit_session_start = make_emitter("session_start")
emit_session_end = make_emitter("session_end", has_reason=True)

emit_block_start = make_indexed_emitter("block_start")
emit_block_end = make_indexed_emitter("block_end", has_reason=True)

emit_trial_start = make_indexed_emitter("trial_start")
emit_trial_end = make_indexed_emitter("trial_end", has_reason=True)

emit_fixation_start = make_emitter("fixation_start")
emit_fixation_end = make_emitter("fixation_end", has_reason=False)

def emit_alignment_start(
        ctx: SessionContext,
    ) -> None:
    ctx.recorder.emit({
        "type": "alignment_start",
        "time": ctx.now()
    })

def emit_alignment_end(
        ctx: SessionContext,
        *,
        t0_device: float | None,
        t0_system: float | None,
        reason: EndReason,
        cause: str | None,
    ) -> None:
    ctx.recorder.emit({
        "type": "alignment_end",
        "time": ctx.now(),
        "t0_device": t0_device,
        "t0_system": t0_system,
        "reason": reason,
        "cause": cause,
    })

