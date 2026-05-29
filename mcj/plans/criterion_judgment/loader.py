import json
from pathlib import Path
from mcj.config.experiment import NUM_BLOCKS
from mcj.stimuli.schema import WordTable
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentPlan,
    CriterionJudgmentBlockPlan,
    CriterionJudgmentCondition,
    CriterionJudgmentTrial
)


from mcj.plans.criterion_judgment.validation import validate_criterion_judgment_plan
from typing import Sequence


def _build_criterion_judgment_plan(data: dict, *, word_table: WordTable):
    def _build_trials(word_sequence, word_table) -> Sequence[CriterionJudgmentTrial]:
        return [
            CriterionJudgmentTrial(
                word=word_table[w].word,
                domain=word_table[w].domain,
                size=word_table[w].size,
                danger=word_table[w].danger,
                orthography=word_table[w].orthography
            )
            for w in word_sequence
        ]

    blocks = [
        CriterionJudgmentBlockPlan(
            block_index=i,
            condition=CriterionJudgmentCondition(data["condition"]),
            trials=_build_trials(block['word_sequence'], word_table) 
        ) for i, block in enumerate(data['blocks'])
    ]
    return CriterionJudgmentPlan(
        subject_id=data['subject_id'],
        blocks=blocks
    )


def load_criterion_judgment_plan(path: Path, word_table: WordTable) -> CriterionJudgmentPlan:
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

    validate_criterion_judgment_plan(data, word_table=word_table)
    return _build_criterion_judgment_plan(data, word_table=word_table)



