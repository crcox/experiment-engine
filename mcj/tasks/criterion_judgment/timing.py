from typing import Sequence

from dataclasses import dataclass

from mcj.runtime.roles import RoleConfig
from mcj.runtime.states import TrialState

@dataclass(frozen=True)
class TrialTiming:
    fixation_on: float | None
    fixation_off: float | None
    stimulus_off: float | None
    feedback_off: float | None

    @property
    def stimulus_on(self):
        return self.fixation_off

    @property
    def feedback_on(self):
        return self.stimulus_off

    @property
    def has_schedule(self):
        return self.fixation_on is not None

    @property
    def has_feedback(self):
        return self.feedback_on is not None

    def get_scheduled_end_time_for_state(self, state: TrialState) -> float | None:
        if state == TrialState.FIXATION:
            return self.fixation_off

        if state == TrialState.STIMULUS:
            return self.stimulus_off

        if state == TrialState.FEEDBACK:
            return self.feedback_off

        raise KeyError(state)

    def __post_init__(self):
        # core schedule consistency
        base = [self.fixation_on, self.fixation_off, self.stimulus_on]
        if any(v is None for v in base) and not all(v is None for v in base):
            raise ValueError("Fixation/stimulus timing must be fully defined or absent")

        # feedback consistency (independent)
        fb = [self.feedback_on, self.feedback_off]
        if any(v is None for v in fb) and not all(v is None for v in fb):
            raise ValueError("Feedback_on/off must both be defined or both None")

def make_empty_schedule(n_trials: int) -> list[TrialTiming]:
    return [
        TrialTiming(
            fixation_on=None,
            fixation_off=None,
            stimulus_off=None,
            feedback_off=None,
        )
        for _ in range(n_trials)
    ]

def build_schedule(t0: float, n_trials: int, role_cfg: RoleConfig) -> Sequence[TrialTiming]:
    # The definition routine only happens in Practice mode, and is always ResponseTermination()
    prompt_duration = role_cfg.prompt_duration_seconds
    fixation_duration = role_cfg.fixation_duration_seconds
    stimulus_duration = role_cfg.stimulus_duration_seconds

    durations: list[float|None] = [prompt_duration, fixation_duration, stimulus_duration]
    
    if role_cfg.feedback is not None:
        feedback_duration = role_cfg.feedback.duration_seconds
        durations.append(feedback_duration)

    schedule_valid = not any(d is None for d in durations)

    if not schedule_valid:
        return make_empty_schedule(n_trials)

    assert prompt_duration is not None
    assert fixation_duration is not None
    assert stimulus_duration is not None

    t = t0
    t += prompt_duration

    schedule = []
    for _ in range(n_trials):
        fixation_on = t
        t += fixation_duration

        fixation_off = t
        t += stimulus_duration

        stimulus_off = t
        if role_cfg.feedback is not None:
            if role_cfg.feedback.duration_seconds is not None:
                t += role_cfg.feedback.duration_seconds
                feedback_off = t
            else:
                feedback_off = None
        else:
            feedback_off = None


        schedule.append(TrialTiming(
            fixation_on=fixation_on,
            fixation_off=fixation_off,
            stimulus_off=stimulus_off,
            feedback_off=feedback_off
        ))

    return schedule
