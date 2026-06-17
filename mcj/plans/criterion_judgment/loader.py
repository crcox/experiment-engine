import json
from mcj.config.paths import paths
from mcj.stimuli.schema import WordTable
from mcj.runtime.roles import PlanRole
from mcj.runtime.ids import make_subject_code
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentBlockPlan,
    CriterionJudgmentCondition,
    CriterionJudgmentTrial
)


from mcj.plans.criterion_judgment.schema import Domain, Size, Danger, Orthography
from mcj.plans.criterion_judgment.validation import validate_criterion_judgment_plan
from typing import Sequence, Any


def _build_criterion_judgment_plan(data: dict[str, Any], *, word_table: WordTable):
    def _build_trials(word_sequence: Sequence[str], word_table: WordTable) -> Sequence[CriterionJudgmentTrial]:
        return [
            CriterionJudgmentTrial(
                word=word_table[w].word,
                domain=Domain(word_table[w].domain),
                size=Size(word_table[w].size),
                danger=Danger(word_table[w].danger),
                orthography=Orthography(word_table[w].orthography)
            )
            for w in word_sequence
        ]

    blocks = [
        CriterionJudgmentBlockPlan(
            block_index=i,
            condition=CriterionJudgmentCondition(block["condition"]),
            trials=_build_trials(block['word_sequence'], word_table) 
        ) for i, block in enumerate(data['blocks'])
    ]
    return CriterionJudgmentPlan(
        subject_id=data['subject_id'],
        left_response=data['left_response'],
        blocks=blocks
    )


def load_criterion_judgment_plan(role: PlanRole, subject_id: int, word_table: WordTable) -> CriterionJudgmentPlan:
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
    
    if role == PlanRole.PRACTICE:
        path = paths.ASSETS / "practice" / "practice.json"
    elif role == PlanRole.MAIN:
        subject_code = make_subject_code(subject_id)
        path = paths.ASSETS / "subjects" / f"{subject_code}.json"
    elif role == PlanRole.DEV:
        path = paths.ASSETS / "practice" / "practice.json"
    else:
        raise RuntimeError(f"Unhandled role {role!r}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    validate_criterion_judgment_plan(data, word_table=word_table)
    return _build_criterion_judgment_plan(data, word_table=word_table)



