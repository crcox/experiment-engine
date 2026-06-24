from __future__ import annotations

from mcj.runtime.environments import Environment
from mcj.runtime.input import InputBackend, InputChannel, AdapterType
from mcj.runtime.profiles import TaskProfile
from mcj.runtime.config_types import TaskProfileConfigs

from mcj.routines.instructions.config import (
    build_instruction_profile_config,
)
from mcj.tasks.criterion_judgment.config import (
    build_practice_profile_config,
    build_main_profile_config,
    build_dev_profile_config,
)


EXPERIMENT_NAME: str = "Multi-Criterion Judgment Task"

ENVIRONMENT_CHANNELS = {
    Environment.PRACTICE: [
        InputChannel.KEYBOARD
    ],
    Environment.SCANNER: [
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


CONFIG_BY_PROFILE: dict[TaskProfile, TaskProfileConfigs]  = {
    TaskProfile.PRACTICE: {
        "instructions": build_instruction_profile_config(),
        "task": build_practice_profile_config(),
    },
    TaskProfile.MAIN: {
        "instructions": build_instruction_profile_config(),
        "task": build_main_profile_config(),
    },
    TaskProfile.DEV: {
        "instructions": build_instruction_profile_config(),
        "task": build_dev_profile_config(),
    },
}

