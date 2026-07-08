from __future__ import annotations

from typing import Sequence

from dataclasses import dataclass

from mcj.runtime.profiles import TaskProfileConfig
from mcj.runtime.states import TrialState

from mcj.tasks.criterion_judgment.actions import CJAction

@dataclass(frozen=True)
class BlockSchedule:
    preamble: PreambleTiming | None = None
    trials: Sequence[TrialTiming] | None = None

@dataclass(frozen=True)
class PreambleTiming:
    prompt_off: float | None 
    definition_off: float | None 

@dataclass(frozen=True)
class TrialTiming:
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

def make_empty_schedule() -> BlockSchedule:
    return BlockSchedule()

def build_schedule(t0: float, n_trials: int, profile_cfg: TaskProfileConfig[CJAction]) -> BlockSchedule:
    # The definition routine only happens in Practice environment, and is always ActionTermination()
    if profile_cfg.timing is None:
        return make_empty_schedule()

    prompt_duration = profile_cfg.timing.prompt_duration_seconds
    definition_duration = profile_cfg.timing.definition_duration_seconds
    fixation_duration = profile_cfg.timing.fixation_duration_seconds
    stimulus_duration = profile_cfg.timing.stimulus_duration_seconds

    required_durations: list[float|None] = [prompt_duration, fixation_duration, stimulus_duration]
    
    if profile_cfg.feedback is not None:
        feedback_duration = profile_cfg.feedback.duration_seconds
        required_durations.append(feedback_duration)

    schedule_valid = not any(d is None for d in required_durations)

    if not schedule_valid:
        return make_empty_schedule()

    assert prompt_duration is not None
    assert fixation_duration is not None
    assert stimulus_duration is not None

    t = t0
    t += prompt_duration
    prompt_off = t
    if definition_duration is not None:
        t += definition_duration
        definition_off = t
    else:
        definition_off = None

    preamble = PreambleTiming(
        prompt_off=prompt_off,
        definition_off=definition_off,
    )

    trials: list[TrialTiming] = []
    for _ in range(n_trials):

        t += fixation_duration
        fixation_off = t

        t += stimulus_duration
        stimulus_off = t

        if profile_cfg.feedback is not None:
            if profile_cfg.feedback.duration_seconds is not None:
                t += profile_cfg.feedback.duration_seconds
                feedback_off = t
            else:
                feedback_off = None
        else:
            feedback_off = None

        trials.append(TrialTiming(
            fixation_off=fixation_off,
            stimulus_off=stimulus_off,
            feedback_off=feedback_off
        ))

    return BlockSchedule(preamble, trials)
