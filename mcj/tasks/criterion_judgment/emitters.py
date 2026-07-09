from __future__ import annotations

from mcj.runtime.emitter_factory import make_emitter
from mcj.runtime.session_context import SessionContext
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.tasks import Task
from mcj.plans.criterion_judgment.schema import (
    CJCondition,
    CJResponse,
)
from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.tasks.criterion_judgment.event_types import CJEventType

# State emitters ----
def emit_condition_set(
    ctx: SessionContext,
    condition: CJCondition
):
    ctx.recorder.emit({
        "type": CJEventType.CONDITION_SET.value,
        "time": ctx.now(),
        "condition": condition.value,
    })

# Instantaneous events ----
def emit_stimulus_onset(
    ctx: SessionContext
):
    ctx.recorder.emit({
        "type": CJEventType.STIMULUS_ONSET.value,
        "time": ctx.now()
    })

def emit_action(
    ctx: SessionContext,
    action: CJAction
):
    ctx.recorder.emit({
        "type": CJEventType.ACTION.value,
        "time": ctx.now(),
        "action": action.value,
    })

def emit_response(
    ctx: SessionContext,
    response: CJResponse
):
    ctx.recorder.emit({
        "type": CJEventType.RESPONSE.value,
        "time": ctx.now(),
        "response": response.value,
    })

def emit_response_mark(
    ctx: SessionContext,
):
    ctx.recorder.emit({
        "type": CJEventType.RESPONSE_MARK.value,
        "time": ctx.now(),
    })



# Bounded Events ----
emit_definition_start = make_emitter(CJEventType.DEFINITION_START.value) 
emit_definition_end = make_emitter(CJEventType.DEFINITION_END.value, has_reason=True) 

emit_prompt_start = make_emitter(CJEventType.PROMPT_START.value) 
emit_prompt_end = make_emitter(CJEventType.PROMPT_END.value, has_reason=True) 

def emit_task_start(
    ctx: SessionContext,
):
    ctx.recorder.emit({
        "type": CJEventType.TASK_START.value,
        "time": ctx.now(),
        "task": Task.CRITERION_JUDGMENT.value,
    })

def emit_task_end(
    ctx: SessionContext,
    reason: EndReason,
    cause: str | None,
):
    ctx.recorder.emit({
        "type": CJEventType.TASK_END.value,
        "time": ctx.now(),
        "reason": reason.value,
        "cause": cause,
    })

def emit_stimulus_start(
    ctx: SessionContext,
    word: str,
    domain: str,
    size: str,
    danger: str,
    orthography: str
):
    ctx.recorder.emit({
        "type": "stimulus_start",
        "time": ctx.now(),
        "word": word,
        "domain": domain,
        "size": size,
        "danger": danger,
        "orthography": orthography
    })

def emit_stimulus_end(
    ctx: SessionContext,
    reason: EndReason,
    cause: str | None,
):
    ctx.recorder.emit({
        "type": "stimulus_end",
        "time": ctx.now(),
        "reason": reason,
        "cause": cause,
    })

def emit_feedback_start(
    ctx: SessionContext,
    feedback: str
):
    ctx.recorder.emit({
        "type": "feedback_start",
        "time": ctx.now(),
        "feedback": feedback,
    })

def emit_feedback_end(
    ctx: SessionContext,
    reason: EndReason,
    cause: str | None,
):
    ctx.recorder.emit({
        "type": "feedback_end",
        "time": ctx.now(),
        "reason": reason,
        "cause": cause,
    })

