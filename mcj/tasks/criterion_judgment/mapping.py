from dataclasses import dataclass
from typing import Mapping

from mcj.runtime.context import RuntimeContext
from mcj.runtime.mapping import EventMapping
from mcj.runtime.modes import Mode
from mcj.runtime.input_events import ButtonEvent
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentResponse as Response,
    CriterionJudgmentResponseSide as ResponseSide,
)
from mcj.tasks.criterion_judgment.actions import CJAction

CODE_TO_SIDE_BY_MODE = {
    Mode.SCANNER: {
        '0': ResponseSide.LEFT,
        '1': ResponseSide.RIGHT,
    },
    Mode.PRACTICE: {
        'f': ResponseSide.LEFT,
        'j': ResponseSide.RIGHT,
    }
}

@dataclass(frozen=True)
class InputActionMapping(EventMapping):
    code_to_side: Mapping[str, ResponseSide]
    side_to_response: Mapping[ResponseSide, Response]

    def interpret(self, event: ButtonEvent) -> CJAction | None:
        side = self.code_to_side.get(event.code)
        if side is None:
            return None
        return self.side_to_response[side]


def make_side_to_response(left_response: Response) -> dict[ResponseSide, Response]:
    if left_response == Response.YES:
        return {
            ResponseSide.LEFT: Response.YES,
            ResponseSide.RIGHT: Response.NO,
        }
    else:
        return {
            ResponseSide.LEFT: Response.NO,
            ResponseSide.RIGHT: Response.YES,
        }


def build_input_mapping(mode: Mode, left_response: Response) -> InputResponseMapping:
    return InputResponseMapping(
        code_to_side=CODE_TO_SIDE_BY_MODE[mode],
        side_to_response=make_side_to_response(left_response),
    )


def build_event_mapping(run_ctx: RuntimeContext) -> InputResponseMapping:
    ctx = run_ctx.ctx
    plan = ctx.get_plan_typed("criterion_judgment", CriterionJudgmentPlan)
    mode = run_ctx.mode
    return build_input_mapping(
        mode=mode,
        left_response=plan.left_response
    )

