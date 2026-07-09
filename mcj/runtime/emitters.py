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
from mcj.runtime.session_context import SessionContext
from mcj.runtime.emitter_factory import make_emitter, make_indexed_emitter
from mcj.runtime.event_types import EventType


# Mechanical Emitters ----
def emit_button_event(
        ctx: SessionContext,
        btn: ButtonEvent
    ) -> None:
    ctx.recorder.emit({
        "type": EventType.BUTTON_EVENT.value,
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
        "type": EventType.SCANNER_TRIGGER.value,
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
        "type": EventType.ENVIRONMENT_SET.value,
        "environment": environment.value,
        "time": ctx.now()
    })

def emit_profile_set(
    ctx: SessionContext,
    profile: ExperimentProfile
):
    ctx.recorder.emit({
        "type": EventType.PROFILE_SET.value,
        "profile": profile.value,
        "time": ctx.now()
    })

def emit_alignment(
        ctx: SessionContext,
        *,
        t0_device: float | None,
        t0_system: float | None,
    ) -> None:
    ctx.recorder.emit({
        "type": EventType.ALIGNMENT.value,
        "time": ctx.now(),
        "t0_device": t0_device,
        "t0_system": t0_system,
    })


# Structural emitters ----
emit_session_start = make_emitter(EventType.SESSION_START.value)
emit_session_end = make_emitter(EventType.SESSION_END.value, has_reason=True)

emit_block_execution_start = make_indexed_emitter(EventType.BLOCK_EXECUTION_START.value)
emit_block_execution_end = make_indexed_emitter(EventType.BLOCK_EXECUTION_END.value, has_reason=True)

emit_block_preamble_start = make_indexed_emitter(EventType.BLOCK_PREAMBLE_START.value)
emit_block_preamble_end = make_indexed_emitter(EventType.BLOCK_PREAMBLE_END.value, has_reason=True)

emit_block_trials_start = make_indexed_emitter(EventType.BLOCK_TRIALS_START.value)
emit_block_trials_end = make_indexed_emitter(EventType.BLOCK_TRIALS_END.value, has_reason=True)

emit_trial_start = make_indexed_emitter(EventType.TRIAL_START.value)
emit_trial_end = make_indexed_emitter(EventType.TRIAL_END.value, has_reason=True)

emit_fixation_start = make_emitter(EventType.FIXATION_START.value)
emit_fixation_end = make_emitter(EventType.FIXATION_END.value, has_reason=False)

emit_auto_triggering_start = make_emitter(EventType.AUTO_TRIGGERING_START.value)
emit_auto_triggering_end = make_emitter(EventType.AUTO_TRIGGERING_END.value, has_reason=False)

emit_wait_for_command_start = make_emitter(EventType.WAIT_FOR_COMMAND_START.value)
emit_wait_for_command_end = make_emitter(EventType.WAIT_FOR_COMMAND_END.value, has_reason=True)

emit_wait_for_trigger_start = make_emitter(EventType.WAIT_FOR_TRIGGER_START.value)
emit_wait_for_trigger_end = make_emitter(EventType.WAIT_FOR_TRIGGER_END.value, has_reason=True)

