from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic

from mcj.runtime.time import Clock

DonePredicate = Callable[[], bool] # True when routine should terminate

ActionT = TypeVar("ActionT")

class TerminationCondition(Generic[ActionT], ABC):

    @abstractmethod
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        action_ref: Callable[[], ActionT | None]
    ) -> DonePredicate:
        pass


class TimeTermination(TerminationCondition[ActionT]):
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        action_ref: Callable[[], ActionT | None]
    ) -> DonePredicate:
        if end_time_seconds is None:
            raise RuntimeError("NonslipTimeTerminations requires end_time_seconds")
            
        def has_elapsed() -> bool:
            return now() >= end_time_seconds 

        return has_elapsed

class ActionTermination(TerminationCondition[ActionT]):
    def __init__(self, terminal_actions: set[ActionT]):
        self.terminal_actions = terminal_actions

    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        action_ref: Callable[[], ActionT | None]
    ) -> DonePredicate:

        if end_time_seconds is not None:
            raise RuntimeError("ActionTermination only checks for a response, and will wait indefinitely. Thus, end_time_second must be None. Did you mean to use ActionOrTimeoutTermination?")

        def has_terminal_action() -> bool:
            print(f"action_ref()={action_ref()}, self.terminal_actions={self.terminal_actions}")
            return action_ref() in self.terminal_actions

        return lambda: has_terminal_action()


class ActionOrTimeoutTermination(TerminationCondition[ActionT]):
    def __init__(self, terminal_actions: set[ActionT]):
        self.terminal_actions = terminal_actions

    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        action_ref: Callable[[], ActionT | None]
    ) -> DonePredicate:
        if end_time_seconds is None:
            raise RuntimeError("ActionOrTimeoutTermination requires end_time_seconds")

        def has_terminal_action() -> bool:
            return action_ref() in self.terminal_actions

        def has_timedout() -> bool:
            return now() >= end_time_seconds

        return lambda: has_terminal_action() or has_timedout()
