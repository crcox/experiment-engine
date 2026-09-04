from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.config_types import TaskConfigBundle
from mcj.runtime.mapping import key_mapping
from mcj.runtime.profiles import TaskProfileConfig
from mcj.runtime.states import InstructionState
from mcj.runtime.termination import ActionTermination


def get_task_config(bundle: TaskConfigBundle) -> TaskProfileConfig[InstructionAction]:
    return bundle["instructions"]


def build_instruction_profile_config() -> TaskProfileConfig[InstructionAction]:
    return TaskProfileConfig(
        termination_by_state={
            InstructionState.INSTRUCTION: ActionTermination(
                {InstructionAction.ADVANCE}
            ),
        },
        action_mapping_by_state={
            InstructionState.INSTRUCTION: key_mapping(
                {"space": InstructionAction.ADVANCE}
            ),
        },
        timing=None,
        feedback=None,
        response_mark=None,
    )
