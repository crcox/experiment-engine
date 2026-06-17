from abc import ABC

class BlockPlan(ABC):
    """
    Base class for all block plans.
    """
    pass

class TaskPlan(ABC):
    """
    Base class for all task plans.
    """
    subject_id: int
