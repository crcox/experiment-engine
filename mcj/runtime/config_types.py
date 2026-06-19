from typing import TypedDict

from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.roles import RoleConfig
from mcj.tasks.criterion_judgment.actions import CJAction

class RoleBundle(TypedDict):
    instructions: RoleConfig[InstructionAction]
    task: RoleConfig[CJAction]


