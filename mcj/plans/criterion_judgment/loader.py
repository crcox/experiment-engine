import json
from pathlib import Path
from mcj.plans.criterion_judgment.schema import CriterionJudgmentCondition
from mcj.plans.criterion_judgment.schema import CriterionJudgmentPlan, CriterionJudgmentBlockPlan
from mcj.plans.criterion_judgment.validation import validate_sequence_mts_plan


def _build_criterion_judgment_plan(data: dict):
    blocks = [
        CriterionJudgmentBlockPlan(
            block_index=i,
            instructions=data["instructions"],
            trials=Sequence[WordTrial]
        )
        for i, block in enumerate(data['blocks'])
    ]
    return CriterionJudgmentPlan(
        subject_id=data['subject_id'],
        condition=CriterionJudgmentCondition(data['condition']),
        blocks=blocks
    )


def load_criterion_judgment_plan(path: Path) -> CriterionJudgmentPlan:
    """
    Load and validate a CriterionJudgmentPlan from a JSON file.

    Parameters:
        path : Path
            Path to a JSON file containing a trial plan.

    Returns:
        SessionPlan
            A validated SessionPlan dictionary.

    Raises:
        CriterionJudgmentPlanError
            If the file is missing required keys or contains invalid types.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    validate_sequence_mts_plan(data)
    return _build_sequence_mts_plan(data)



