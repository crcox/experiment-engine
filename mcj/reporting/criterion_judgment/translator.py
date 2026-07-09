from dataclasses import dataclass
from typing import Sequence

from mcj.plans.criterion_judgment.schema import (
        RESPONSE_TO_ATTRIBUTE_BY_CONDITION,
        CJCondition,
        CJResponse,
    )
from mcj.reporting.criterion_judgment.schema import (
        is_condition_set_event,
        is_response_event,
        is_stimulus_onset_event,
        is_stimulus_start_event,
    )
from mcj.reporting.schema import (
        is_block_execution_start_event,
        is_trial_end_event,
        is_trial_start_event,
    )
from mcj.runtime.events import EventDict

@dataclass
class TrialRecord:
    block_index: int
    trial_index: int

    condition: str | None

    word: str | None
    domain: str | None
    size: str | None
    danger: str | None
    orthography: str | None

    stimulus_onset_time: float | None

    response: str | None
    response_meaning: str | None
    response_time: float | None

    is_correct: bool | None

    rt_ms: float | None
    responded: bool

    trial_reason: str | None
    trial_cause: str | None

class TrialLogTranslator:
    def __init__(self):
        self._records: list[TrialRecord] = []

        self._current_condition: str | None = None
        self._current_block_index: int | None = None

        self._current_trial: TrialRecord | None = None

    def consume(self, event: EventDict) -> None:
        # --------------------
        # Block metadata
        # --------------------

        if is_condition_set_event(event):
            self._current_condition = event["condition"]
            return

        if is_block_execution_start_event(event):
            self._current_block_index = event["index"]
            return

        # --------------------
        # Trial metadata
        # --------------------

        if is_trial_start_event(event):
            self._current_trial = TrialRecord(
                block_index=self._current_block_index or 0,
                trial_index=event["index"],

                condition=self._current_condition,

                word=None,
                domain=None,
                size=None,
                danger=None,
                orthography=None,

                stimulus_onset_time=None,

                response=None,
                response_meaning=None,
                response_time=None,

                is_correct=None,

                rt_ms=None,
                responded=False,

                trial_reason=None,
                trial_cause=None,
            )
            return

        # --------------------
        # Stimulus metadata
        # --------------------

        if (
            is_stimulus_start_event(event)
            and self._current_trial is not None
        ):
            self._current_trial.word = event["word"]
            self._current_trial.domain = event["domain"]
            self._current_trial.size = event["size"]
            self._current_trial.danger = event["danger"]
            self._current_trial.orthography = event["orthography"]
            return

        if (
            is_stimulus_onset_event(event)
            and self._current_trial is not None
        ):
            self._current_trial.stimulus_onset_time = event["time"]
            return

        # --------------------
        # Response
        # --------------------

        if (
            is_response_event(event)
            and self._current_trial is not None
        ):
            self._current_trial.response = event["response"]

            if self._current_condition is not None:
                self._current_trial.response_meaning = response_meaning(
                    CJResponse(self._current_trial.response),
                    CJCondition(self._current_condition),
                )

            if self._current_condition is not None:
                self._current_trial.is_correct = is_correct(self._current_trial)

            self._current_trial.response_time = event["time"]
            self._current_trial.responded = True

            if self._current_trial.stimulus_onset_time is not None:
                self._current_trial.rt_ms = (
                    event["time"]
                    - self._current_trial.stimulus_onset_time
                ) * 1000.0

            return

        # --------------------
        # Trial completion
        # --------------------

        if (
            is_trial_end_event(event)
            and self._current_trial is not None
        ):
            self._current_trial.trial_reason = event["reason"]
            self._current_trial.trial_cause = event["cause"]

            self._records.append(self._current_trial)
            self._current_trial = None
            return

    @property
    def records(self) -> list:
        return list(self._records)

def response_meaning(response: CJResponse, condition: CJCondition) -> str:
    return RESPONSE_TO_ATTRIBUTE_BY_CONDITION[condition][response].value


def is_correct(trial: TrialRecord) -> bool | None:
    if trial.condition is None:
        raise RuntimeError("The condition for this trial has not been identified.")

    if trial.response is None:
        return None

    if trial.response_meaning is None:
        i = trial.trial_index
        raise RuntimeError(f"There was no interpretation for the current trial's response ({i}).")

    target = getattr(trial, trial.condition)

    return trial.response_meaning == target


def translate(events: Sequence[EventDict]) -> list[TrialRecord]:
    translator = TrialLogTranslator()

    for event in events:
        translator.consume(event)

    return translator.records

