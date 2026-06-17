from dataclasses import dataclass

from mcj.runtime.termination import TerminationCondition
from mcj.runtime.mapping import EventMappingFactory


@dataclass(frozen=True)
class ScreenConfig:
    completion: TerminationCondition
    event_mapping_factory: EventMappingFactory

