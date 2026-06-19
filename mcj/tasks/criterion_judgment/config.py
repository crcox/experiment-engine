from dataclasses import dataclass
from pathlib import Path

from mcj.runtime.config_types import RoleBundle
from mcj.runtime.roles import RoleConfig, FeedbackConfig, FeedbackStimulusConfig, ResponseMarkConfig
from mcj.runtime.mapping import key_mapping, dynamic_mapping, no_op
from mcj.runtime.states import TrialState, PromptState, DefinitionState
from mcj.runtime.termination import TimeTermination, ActionTermination, ActionOrTimeoutTermination

from mcj.tasks.criterion_judgment.mapping import build_action_mapping
from mcj.tasks.criterion_judgment.actions import CJAction


@dataclass(frozen=True)
class CriterionJudgmentTaskConfig:
    instructions_path: Path

def get_task_config(bundle: RoleBundle) -> RoleConfig[CJAction]:
    return bundle["task"]

def build_practice_role_config() -> RoleConfig[CJAction]:
    return RoleConfig(
        termination_by_state={
            PromptState.PROMPT: ActionTermination({CJAction.ADVANCE}),
            DefinitionState.DEFINITION: ActionTermination({CJAction.ADVANCE}),
            TrialState.FIXATION: TimeTermination(),
            TrialState.STIMULUS: ActionOrTimeoutTermination({CJAction.LEFT, CJAction.RIGHT}),
            TrialState.FEEDBACK: TimeTermination()
        },
        action_mapping_by_state={
            PromptState.PROMPT: key_mapping({"space": CJAction.ADVANCE}),
            DefinitionState.DEFINITION: key_mapping({"space": CJAction.ADVANCE}),
            TrialState.FIXATION: no_op(),
            TrialState.STIMULUS: dynamic_mapping(build_action_mapping), 
            TrialState.FEEDBACK: no_op(),
        },
        prompt_duration_seconds=None,
        fixation_duration_seconds=4.0,
        stimulus_duration_seconds=2.0,
        response_mark=None,
        feedback=FeedbackConfig(
            duration_seconds=1.0,
            stimulus_correct=FeedbackStimulusConfig("Correct", "green"),
            stimulus_incorrect=FeedbackStimulusConfig("Incorrect", "red"),
            stimulus_timeout=FeedbackStimulusConfig("Too slow", "red"),
        )
    )


def build_main_role_config() -> RoleConfig[CJAction]:
    return RoleConfig(
        termination_by_state={
            PromptState.PROMPT: TimeTermination(),
            TrialState.FIXATION: TimeTermination(),
            TrialState.STIMULUS: TimeTermination(),
            TrialState.FEEDBACK: TimeTermination()
        },
        action_mapping_by_state={
            PromptState.PROMPT:  no_op(),
            TrialState.FIXATION: no_op(),
            TrialState.STIMULUS: dynamic_mapping(build_action_mapping),
            TrialState.FEEDBACK: no_op(),
        },
        prompt_duration_seconds = 12.0,
        fixation_duration_seconds =  4.0,
        stimulus_duration_seconds =  2.0,
        response_mark = ResponseMarkConfig(),
        feedback = None
    )


def build_dev_role_config() -> RoleConfig[CJAction]:
    return RoleConfig(
        termination_by_state={
            PromptState.PROMPT: ActionTermination({CJAction.ADVANCE}),
            DefinitionState.DEFINITION: ActionTermination({CJAction.ADVANCE}),
            TrialState.FIXATION: ActionTermination({CJAction.ADVANCE}),
            TrialState.STIMULUS: ActionTermination({CJAction.LEFT, CJAction.RIGHT}),
            TrialState.FEEDBACK: ActionTermination({CJAction.ADVANCE}),
        },
        action_mapping_by_state={
            PromptState.PROMPT: key_mapping({"space": CJAction.ADVANCE}),
            DefinitionState.DEFINITION: key_mapping({"space": CJAction.ADVANCE}),
            TrialState.FIXATION: key_mapping({"space": CJAction.ADVANCE}),
            TrialState.STIMULUS: dynamic_mapping(build_action_mapping),
            TrialState.FEEDBACK: key_mapping({"space": CJAction.ADVANCE}),
        },
        prompt_duration_seconds = None,
        fixation_duration_seconds = None,
        stimulus_duration_seconds = None,
        response_mark = None,
        feedback = FeedbackConfig(
            duration_seconds = None,
            stimulus_correct = FeedbackStimulusConfig(
                text="Correct",
                color="green",
            ),
            stimulus_incorrect = FeedbackStimulusConfig(
                text="Incorrect",
                color="red",
            ),
            stimulus_timeout = FeedbackStimulusConfig(
                text="Too slow",
                color="red",
            )
        )
    )
