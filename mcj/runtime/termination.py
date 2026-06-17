from abc import ABC, abstractmethod
from typing import Callable

from mcj.runtime.time import Clock

DonePredicate = Callable[[], bool] # True when routine should terminate

class TerminationCondition(ABC):

    @abstractmethod
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        response_recorded_ref: Callable[[], bool]
    ) -> DonePredicate:
        pass


class TimeTermination(TerminationCondition):
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        response_recorded_ref: Callable[[], bool]
    ) -> DonePredicate:
        if end_time_seconds is None:
            raise RuntimeError("NonslipTimeTerminations requires end_time_seconds")
            
        def has_elapsed() -> bool:
            return now() >= end_time_seconds 

        return has_elapsed

class ResponseTermination(TerminationCondition):
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        response_recorded_ref: Callable[[], bool]
    ) -> DonePredicate:

        if end_time_seconds is not None:
            raise RuntimeError("ResponseTermination only checks for a response, and will wait indefinitely. Thus, end_time_second must be None. Did you mean to use ResponseOrTimeoutTermination?")

        def has_response() -> bool:
            return response_recorded_ref()

        return has_response


class ResponseOrTimeoutTermination(TerminationCondition):
    def make_done_predicate(
        self,
        now: Clock, *,
        end_time_seconds: float | None,
        response_recorded_ref: Callable[[], bool]
    ) -> DonePredicate:
        if end_time_seconds is None:
            raise RuntimeError("ResponseOrTimeoutTermination requires end_time_seconds")

        def has_response() -> bool:
            return response_recorded_ref()

        def has_timedout() -> bool:
            return now() >= end_time_seconds

        return lambda: has_response() or has_timedout()
