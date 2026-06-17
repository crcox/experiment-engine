from typing import Callable

from mcj.runtime.context import RuntimeContext, SessionContext
from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.roles import RoleConfig
from mcj.runtime.states import TrialState
from mcj.runtime.termination import DonePredicate
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import EscapePressed
from mcj.runtime.input_events import ButtonEvent, TriggerEvent
from mcj.components.fixation import FixationDisplay

from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentTrial as Trial,
    CriterionJudgmentResponse as Response,
    CriterionJudgmentResponseSide as ResponseSide,
)
from mcj.plans.criterion_judgment.prompts_loader import load_prompt
from mcj.tasks.criterion_judgment.timing import TrialTiming
from mcj.tasks.criterion_judgment.mapping import (
    EventMapping,
    InputResponseMapping,
)
from mcj.tasks.criterion_judgment.display import (
    CriterionJudgmentStimulusDisplay as StimulusDisplay,
    CriterionJudgmentFeedbackDisplay as FeedbackDisplay,

)
from mcj.runtime.emitters import (
    emit_button_event, emit_scanner_trigger,
    emit_trial_start, emit_trial_end,
    emit_fixation_start, emit_fixation_end,
)
from mcj.tasks.criterion_judgment.emitters import (
    emit_stimulus_start, emit_stimulus_end,
    emit_feedback_start, emit_feedback_end,
    emit_response, emit_stimulus_onset,
    emit_response_mark,
)

def emit_state_end(ctx: SessionContext, state: TrialState, reason: EndReason, cause: str | None) -> None:
    if state == TrialState.FIXATION:
        emit_fixation_end(ctx)
    elif state == TrialState.STIMULUS:
        emit_stimulus_end(ctx, reason, cause)
    elif state == TrialState.FEEDBACK:
        emit_feedback_end(ctx, reason, cause)


def run_trial(
    factory: StimFactory,
    trial: Trial,
    *,
    block_index: int,
    trial_index: int,
    trial_timing: TrialTiming,
    run_ctx: RuntimeContext,
) -> None:
    ctx = run_ctx.ctx
    role_cfg = run_ctx.role_cfg

    # --- Build or select trial configuration ---
    plan = run_ctx.ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)
    block_plan = plan.blocks[block_index]
    condition = block_plan.condition
    expected_response = trial.expected_response(condition)
    prompt = load_prompt(condition)
    
    # --- Initialize displays
    fixation_display = FixationDisplay(factory)
    stimulus_display = StimulusDisplay(factory, role_cfg.response_mark)
    feedback_display = FeedbackDisplay(factory)

    # --- Define how states transition ---
    def get_next_state(state: TrialState, role_cfg: RoleConfig) -> TrialState:
        if state == TrialState.FIXATION:
            return TrialState.STIMULUS

        if state == TrialState.STIMULUS:
            if role_cfg.provide_feedback:
                return TrialState.FEEDBACK
            return TrialState.DONE

        if state == TrialState.FEEDBACK:
            return TrialState.DONE

        raise RuntimeError(f"Unhandled state: {state}")

    # --- Define what each state is ---
    def enter_state(state: TrialState, prev_state_had_response: bool, prev_response: Response | None) -> tuple[EventMapping, DonePredicate, Callable[[], None]]:
        mapping_factory = role_cfg.event_mapping_by_state[state]
        mapping = mapping_factory(run_ctx)
        scheduled_end_time = trial_timing.get_scheduled_end_time_for_state(state)
        termination = role_cfg.termination_by_state[state]
        done = termination.make_done_predicate(
            ctx.now,
            end_time_seconds=scheduled_end_time,
            response_recorded_ref=lambda: prev_state_had_response
        )

        if state == TrialState.FIXATION:
            emit_fixation_start(ctx)
            draw = fixation_display.draw

        elif state == TrialState.STIMULUS:
            stimulus_display.clear_response_mark()

            assert isinstance(mapping, InputResponseMapping)
            stimulus_display.update(
                cue_text=trial.word,
                prompt_text=prompt.prompt,
                left_text=mapping.side_to_response[ResponseSide.LEFT].value,
                right_text=mapping.side_to_response[ResponseSide.RIGHT].value
            )
            draw = stimulus_display.draw
            emit_stimulus_start(
                ctx,
                trial.word,
                trial.domain.value,
                trial.size.value,
                trial.danger.value,
                trial.orthography.value
            )
            factory.call_on_flip(emit_stimulus_onset, ctx)

        elif state == TrialState.FEEDBACK and role_cfg.feedback is not None:
            feedback_cfg = role_cfg.feedback
            if prev_state_had_response:
                if expected_response == prev_response:
                    feedback_stimulus_cfg = feedback_cfg.stimulus_correct
                else:
                    feedback_stimulus_cfg = feedback_cfg.stimulus_incorrect
            else:
                feedback_stimulus_cfg = feedback_cfg.stimulus_timeout

            feedback_display.update(feedback_stimulus_cfg)
            draw = feedback_display.draw
            emit_feedback_start(ctx, feedback_stimulus_cfg.text)
        else:
            raise RuntimeError(f"Unhandled state {state}.")

        return mapping, done, draw


    # --- Start Trial ---
    emit_trial_start(ctx, trial_index)
    response_received = False
    response = None
    end_reason = EndReason.COMPLETE
    end_cause = None

    state = TrialState.FIXATION
    mapping, done, draw = enter_state(
        state,
        prev_state_had_response=response_received,
        prev_response=response
    )

    try:
        while state != TrialState.DONE:

            # --- update input ---
            ctx.input.update()

            # --- process mechanical events ---
            events = ctx.input.pop_events()
            for event in events:
                if isinstance(event, TriggerEvent):
                    emit_scanner_trigger(ctx, event)

                elif isinstance(event, ButtonEvent):
                    emit_button_event(ctx, event)

                    if event.code == "escape":
                        end_reason = EndReason.ABORTED
                        raise EscapePressed

                    result = mapping.interpret(event)
                    if result is not None and not response_received:
                        response = Response(result)
                        emit_response(ctx, response)
                        response_received = True

                        if role_cfg.should_show_response_mark(state):
                            emit_response_mark(ctx)
                            stimulus_display.mark_response(response.value)
                else:
                    RuntimeError(f"Unhandled event type {event}")

            # --- draw ---
            draw()
            factory.flip()

            # --- state transitions ---
            if done():
                emit_state_end(ctx, state, end_reason, end_cause)
                state = get_next_state(state, role_cfg)

                if state != TrialState.DONE:
                    mapping, done, draw = enter_state(
                        state,
                        prev_state_had_response=response_received,
                        prev_response=response
                    )
                    response_received = False
                    response = None


    except EscapePressed as e:
        end_reason = EndReason.ABORTED
        end_cause = "escape_key"
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_trial_end(
            ctx,
            index=trial_index,
            reason=end_reason,
            cause=end_cause
        )


