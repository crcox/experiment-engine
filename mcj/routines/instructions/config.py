from mcj.runtime.config_types import RoleBundle
from mcj.runtime.roles import RoleConfig
from mcj.runtime.states import InstructionState
from mcj.runtime.mapping import key_mapping
from mcj.runtime.termination import ActionTermination
from mcj.routines.instructions.actions import InstructionAction

def get_task_config(bundle: RoleBundle) -> RoleConfig[InstructionAction]:
    return bundle["instructions"]

def build_instruction_role_config() -> RoleConfig[InstructionAction]:
    return RoleConfig(
        termination_by_state={
            InstructionState.INSTRUCTION: ActionTermination({InstructionAction.ADVANCE}),
        },
        action_mapping_by_state={
            InstructionState.INSTRUCTION: key_mapping({"space": InstructionAction.ADVANCE}),
        },
        prompt_duration_seconds=None,
        fixation_duration_seconds=None,
        stimulus_duration_seconds=None,
        feedback=None,
        response_mark=None,
    )
