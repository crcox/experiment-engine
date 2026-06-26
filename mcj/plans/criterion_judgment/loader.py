import json
from pathlib import Path
from mcj.config.paths import paths
from mcj.stimuli.schema import WordTable
from mcj.runtime.profiles import ExperimentProfile
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


def _build_criterion_judgment_plan(data: dict[str, Any], *, profile: ExperimentProfile, word_table: WordTable):
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

    if profile.requires_subject_id:
        subject_id = data['subject_id']
    else:
        subject_id = None

    return CriterionJudgmentPlan(
        subject_id=subject_id,
        left_response=data['left_response'],
        blocks=blocks,
    )


def load_criterion_judgment_plan(
    profile_assets_dir: Path,
    profile: ExperimentProfile,
    subject_id: int | None,
    word_table: WordTable
) -> CriterionJudgmentPlan:

    if profile.requires_subject_id:
        if subject_id is None:
            raise RuntimeError(f"A subject ID is required when loading a CriterionJudgmentPlan under the {profile.value} profile.")

        subject_code = make_subject_code(subject_id)
        path = profile_assets_dir / f"{subject_code}.json"

    else:
        path = profile_assets_dir / "plan.json"
    
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    validate_criterion_judgment_plan(data, profile=profile, word_table=word_table)
    return _build_criterion_judgment_plan(data, profile=profile, word_table=word_table)



