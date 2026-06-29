from typing import Callable

from mcj.runtime.execution import ExecutionContext
from mcj.runtime.session import SessionContext
from mcj.runtime.display_primitives import StimFactory
from mcj.runtime.profiles import TaskProfileConfig
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
from mcj.tasks.criterion_judgment.actions import CJAction
from mcj.tasks.criterion_judgment.mapping import (
    ActionMapping,
    InputActionMapping,
    make_side_to_response,
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
    emit_response_mark, emit_action
)
from mcj.tasks.common.state_refs import ActionRef

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
    run_ctx: ExecutionContext[CJAction],
) -> None:
    session = run_ctx.session
    ctx = session.ctx
    profile_cfg = run_ctx.profile_cfg

    # --- Build or select trial configuration ---
    plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)
    block_plan = plan.blocks[block_index]
    condition = block_plan.condition
    expected_response = trial.expected_response(condition)
    prompt = load_prompt(condition)

    side_to_response = make_side_to_response(plan.left_response)
    
    # --- Initialize displays
    fixation_display = FixationDisplay(factory)
    stimulus_display = StimulusDisplay(factory, profile_cfg.response_mark)
    feedback_display = FeedbackDisplay(factory)

    # --- Define how states transition ---
    def get_next_state(state: TrialState, profile_cfg: TaskProfileConfig[CJAction]) -> TrialState:
        if state == TrialState.FIXATION:
            return TrialState.STIMULUS

        if state == TrialState.STIMULUS:
            if profile_cfg.has_feedback_cfg and session.environment.allows_feedback:
                return TrialState.FEEDBACK
            return TrialState.DONE

        if state == TrialState.FEEDBACK:
            return TrialState.DONE

        raise RuntimeError(f"Unhandled state: {state}")

    # --- Define what each state is ---
    def enter_state(state: TrialState, last_action: ActionRef[CJAction], prev_response: Response | None) -> tuple[ActionMapping[CJAction], DonePredicate, Callable[[], None]]:
        mapping_factory = profile_cfg.action_mapping_by_state[state]
        mapping = mapping_factory(session)
        scheduled_end_time = trial_timing.get_scheduled_end_time_for_state(state)
        termination = profile_cfg.termination_by_state[state]
        done = termination.make_done_predicate(
            ctx.now,
            end_time_seconds=scheduled_end_time,
            action_ref=lambda: last_action.get()
        )

        if state == TrialState.FIXATION:
            emit_fixation_start(ctx)
            draw = fixation_display.draw

        elif state == TrialState.STIMULUS:
            stimulus_display.clear_response_mark()

            assert isinstance(mapping, InputActionMapping)
            stimulus_display.update(
                cue_text=trial.word,
                prompt_text=prompt.prompt,
                left_text=side_to_response[ResponseSide.LEFT].value,
                right_text=side_to_response[ResponseSide.RIGHT].value
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

        elif state == TrialState.FEEDBACK and profile_cfg.feedback is not None:
            feedback_cfg = profile_cfg.feedback
            if last_action.get() in (CJAction.LEFT, CJAction.RIGHT):
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

    action: CJAction | None = None
    last_action = ActionRef[CJAction]()

    response: Response | None = None

    end_reason = EndReason.COMPLETE
    end_cause = None

    state = TrialState.FIXATION
    mapping, done, draw = enter_state(
        state,
        last_action=last_action,
        prev_response=response
    )

    try:
        while state != TrialState.DONE:

            # --- update input ---
            session.maybe_step_simulation()
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

                    action = mapping.interpret(event)
                    if action is not None and last_action.get() is None:
                        last_action.set(action)
                        emit_action(ctx, action)

                        if last_action.get() in (CJAction.LEFT, CJAction.RIGHT):
                            assert isinstance(mapping, InputActionMapping)

                            side = ResponseSide.LEFT if action == CJAction.LEFT else ResponseSide.RIGHT
                            response = side_to_response[side]

                            emit_response(ctx, response)

                            if profile_cfg.should_show_response_mark(state):
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
                state = get_next_state(state, profile_cfg)

                if state != TrialState.DONE:
                    mapping, done, draw = enter_state(
                        state,
                        last_action=last_action,
                        prev_response=response
                    )
                    last_action.clear()
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


