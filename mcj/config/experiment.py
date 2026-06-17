from __future__ import annotations

from mcj.runtime.mapping import KeyPressMapping, NoOpMapping
from mcj.runtime.modes import Mode
from mcj.runtime.roles import (
    PlanRole,
    RoleConfig,
    FeedbackConfig,
    FeedbackStimulusConfig,
    ResponseMarkConfig,
)
from mcj.runtime.input import InputBackend, InputChannel, AdapterType
from mcj.runtime.states import TrialState, PromptState, DefinitionState, InstructionState
from mcj.runtime.termination import (
    TimeTermination,
    ResponseTermination,
    ResponseOrTimeoutTermination
)

from mcj.tasks.criterion_judgment.mapping import build_event_mapping


EXPERIMENT_NAME: str = "Multi-Criterion Judgment Task"

MODE_CHANNELS = {
    Mode.PRACTICE: [
        InputChannel.KEYBOARD
    ],
    Mode.SCANNER: [
        InputChannel.KEYBOARD,
        InputChannel.CEDRUS,
    ],
}

CHANNEL_IMPLEMENTATIONS = {
    InputChannel.KEYBOARD: {
        InputBackend.REAL: AdapterType.KEYBOARD,
        InputBackend.MOCKED: AdapterType.KEYBOARD,
    },
    InputChannel.CEDRUS: {
        InputBackend.REAL: AdapterType.CEDRUS,
        InputBackend.MOCKED: AdapterType.CEDRUS_MOCK,
    },
}

CONFIG_BY_ROLE = {
    PlanRole.PRACTICE: RoleConfig(
        termination_by_state={
            InstructionState.INSTRUCTION: ResponseTermination(),
            PromptState.PROMPT: ResponseTermination(),
            DefinitionState.DEFINITION: ResponseTermination(),
            TrialState.FIXATION: TimeTermination(),
            TrialState.STIMULUS: ResponseOrTimeoutTermination(),
            TrialState.FEEDBACK: TimeTermination()
        },
        event_mapping_by_state={
            InstructionState.INSTRUCTION:  lambda _: KeyPressMapping({"space"}),
            PromptState.PROMPT:  lambda _: KeyPressMapping({"space"}),
            DefinitionState.DEFINITION:  lambda _: KeyPressMapping({"space"}),
            TrialState.FIXATION: lambda _: NoOpMapping(),
            TrialState.STIMULUS: lambda run_ctx: build_event_mapping(run_ctx),
            TrialState.FEEDBACK: lambda _: NoOpMapping()
        },
        prompt_duration_seconds = None,
        fixation_duration_seconds = 4.0,
        stimulus_duration_seconds = 2.0,
        response_mark = None,
        feedback = FeedbackConfig(
            duration_seconds = 1.0,
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
    ),
    PlanRole.MAIN: RoleConfig(
        termination_by_state={
            InstructionState.INSTRUCTION: ResponseTermination(),
            PromptState.PROMPT: TimeTermination(),
            TrialState.FIXATION: TimeTermination(),
            TrialState.STIMULUS: TimeTermination(),
            TrialState.FEEDBACK: TimeTermination()
        },
        event_mapping_by_state={
            InstructionState.INSTRUCTION:  lambda _: KeyPressMapping({"space"}),
            PromptState.PROMPT:  lambda _: NoOpMapping(),
            TrialState.FIXATION: lambda _: NoOpMapping(),
            TrialState.STIMULUS: lambda run_ctx: build_event_mapping(run_ctx),
            TrialState.FEEDBACK: lambda _: NoOpMapping()
        },
        prompt_duration_seconds = 12.0,
        fixation_duration_seconds =  4.0,
        stimulus_duration_seconds =  2.0,
        response_mark = ResponseMarkConfig(),
        feedback = None
    ),
    PlanRole.DEV: RoleConfig(
        termination_by_state={
            InstructionState.INSTRUCTION: ResponseTermination(),
            PromptState.PROMPT: ResponseTermination(),
            DefinitionState.DEFINITION: ResponseTermination(),
            TrialState.FIXATION: ResponseTermination(),
            TrialState.STIMULUS: ResponseTermination(),
            TrialState.FEEDBACK: ResponseTermination(),
        },
        event_mapping_by_state={
            InstructionState.INSTRUCTION:  lambda _: KeyPressMapping({"space"}),
            PromptState.PROMPT:  lambda _: KeyPressMapping({"space"}),
            DefinitionState.DEFINITION:  lambda _: KeyPressMapping({"space"}),
            TrialState.FIXATION: lambda _: KeyPressMapping({"space"}),
            TrialState.STIMULUS: lambda run_ctx: build_event_mapping(run_ctx),
            TrialState.FEEDBACK: lambda _: KeyPressMapping({"space"}),
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
    ),
}

