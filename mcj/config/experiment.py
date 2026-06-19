from __future__ import annotations

from mcj.runtime.modes import Mode
from mcj.runtime.input import InputBackend, InputChannel, AdapterType
from mcj.runtime.roles import PlanRole
from mcj.runtime.config_types import RoleBundle

from mcj.routines.instructions.config import (
    build_instruction_role_config,
)
from mcj.tasks.criterion_judgment.config import (
    build_practice_role_config,
    build_main_role_config,
    build_dev_role_config,
)


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


CONFIG_BY_ROLE: dict[PlanRole, RoleBundle]  = {
    PlanRole.PRACTICE: {
        "instructions": build_instruction_role_config(),
        "task": build_practice_role_config(),
    },
    PlanRole.MAIN: {
        "instructions": build_instruction_role_config(),
        "task": build_main_role_config(),
    },
    PlanRole.DEV: {
        "instructions": build_instruction_role_config(),
        "task": build_dev_role_config(),
    },
}

