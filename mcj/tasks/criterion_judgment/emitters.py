from __future__ import annotations

from mcj.runtime.emitter_factory import make_emitter
from mcj.runtime.context import SessionContext
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.tasks import Task
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentCondition,
    CriterionJudgmentResponse
)

# State emitters ----
def emit_condition_set(
    ctx: SessionContext,
    condition: CriterionJudgmentCondition
):
    ctx.recorder.emit({
        "type": "condition_set",
        "time": ctx.now(),
        "mode": condition.value,
    })

# Instantaneous events ----
def emit_stimulus_onset(
    ctx: SessionContext
):
    ctx.recorder.emit({
        "type": "stimulus_onset",
        "time": ctx.now()
    })

def emit_response(
    ctx: SessionContext,
    response: CriterionJudgmentResponse
):
    ctx.recorder.emit({
        "type": "response",
        "time": ctx.now(),
        "response": response.value,
    })

def emit_response_mark(
    ctx: SessionContext,
):
    ctx.recorder.emit({
        "type": "response",
        "time": ctx.now(),
    })



# Bounded Events ----
emit_definition_start = make_emitter("definition_start") 
emit_definition_end = make_emitter("definition_end", has_reason=True) 

emit_prompt_start = make_emitter("prompt_start") 
emit_prompt_end = make_emitter("prompt_end", has_reason=True) 

def emit_task_start(
    ctx: SessionContext,
):
    ctx.recorder.emit({
        "type": "task_start",
        "time": ctx.now(),
        "task": Task.CRITERION_JUDGMENT.value,
    })

def emit_task_end(
    ctx: SessionContext,
    reason: EndReason,
    cause: str | None,
):
    ctx.recorder.emit({
        "type": "task_end",
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

