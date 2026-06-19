from dataclasses import dataclass
from typing import Mapping

from mcj.runtime.session import SessionRuntime
from mcj.runtime.mapping import ActionMapping
from mcj.runtime.modes import Mode
from mcj.runtime.input_events import ButtonEvent
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentResponse as Response,
    CriterionJudgmentResponseSide as ResponseSide,
)
from mcj.tasks.criterion_judgment.actions import CJAction

CODE_TO_SIDE_BY_MODE = {
    Mode.SCANNER: {
        '0': ResponseSide.LEFT,
        '2': ResponseSide.RIGHT,
    },
    Mode.PRACTICE: {
        'f': ResponseSide.LEFT,
        'j': ResponseSide.RIGHT,
    }
}

@dataclass(frozen=True)
class InputActionMapping(ActionMapping[CJAction]):
    code_to_side: Mapping[str, ResponseSide]

    def interpret(self, event: ButtonEvent) -> CJAction | None:
        side = self.code_to_side.get(event.code)
        if side is None:
            return None

        if side == ResponseSide.LEFT:
            return CJAction.LEFT
        else:
            return CJAction.RIGHT


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


def build_action_mapping(session: SessionRuntime) -> InputActionMapping:
    return InputActionMapping(
        code_to_side=CODE_TO_SIDE_BY_MODE[session.mode],
    )

