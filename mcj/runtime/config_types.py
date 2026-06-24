from typing import TypedDict

from mcj.routines.instructions.actions import InstructionAction
from mcj.runtime.profiles import TaskProfileConfig
from mcj.tasks.criterion_judgment.actions import CJAction

class TaskProfileConfigs(TypedDict):
    instructions: TaskProfileConfig[InstructionAction]
    task: TaskProfileConfig[CJAction]


