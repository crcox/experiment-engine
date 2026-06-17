from __future__ import annotations

from typing import Any
from mcj.runtime.exceptions import CriterionJudgmentPlanError
from mcj.plans.criterion_judgment.schema import CriterionJudgmentCondition
from mcj.stimuli.schema import WordTable


def _validate_subject_id(data: dict[str, Any]) -> None:
    subject_id = data["subject_id"]
    if not isinstance(subject_id, int):
        raise CriterionJudgmentPlanError(
            f"`subject_id` must be an integer; got {type(subject_id).__name__!r}"
        )


def _validate_condition(raw:  Any) -> None:
    if not isinstance(raw, str):
        raise CriterionJudgmentPlanError(
            f"`condition` must be a string; got {type(raw).__name__!r}"
        )

    CriterionJudgmentCondition(raw)


def _validate_word_sequence(
    word_sequence: list[str],
    *,
    word_table: WordTable,
    context: str
) -> None:
    valid_words = set(word_table.keys())
    seq_words = set(word_sequence)

    invalid_words = seq_words - valid_words
    if invalid_words:
        raise CriterionJudgmentPlanError(
            f"`{context}` contains invalid word strings: "
            f"{sorted(invalid_words)}"
        )

def _validate_session_plan(data: dict[str, Any]) -> None:
    required_keys = {
        "subject_id",
        "left_response",
        "blocks"
    }

    missing = required_keys - data.keys()
    if missing:
        raise CriterionJudgmentPlanError(
            f"SessionPlan is missing required keys: {sorted(missing)}"
        )

def _validate_block_plan(data: dict[str, Any], *, word_table: WordTable) -> None:
    blocks = data["blocks"]
    if not isinstance(blocks, list):
        raise CriterionJudgmentPlanError("`blocks` must be a list[dict[str, list[str]]]")

    for block in blocks:
        if not isinstance(block, dict):
            raise CriterionJudgmentPlanError("Each `block` must be a dict[str, list[str]]")

        if "condition" not in block:
            raise CriterionJudgmentPlanError("Each `block` dict must have key 'condition'")

        _validate_condition(block["condition"])

        if "word_sequence" not in block:
            raise CriterionJudgmentPlanError("Each `block` dict must have key 'word_sequence'")

        if not isinstance(block["word_sequence"], list):
            raise CriterionJudgmentPlanError("`block['word_sequence']` must be list[str]")


    for i,block in enumerate(blocks):
        _validate_word_sequence(
            block["word_sequence"],
            word_table=word_table,
            context=f"blocks[{i}]['word_sequence']"
        )


def validate_criterion_judgment_plan(data: dict[str, Any], word_table: WordTable) -> None:
    """
    Validate the structure and contents of a session plan dictionary.

    Raises:
        CriterionJudgmentPlanError on first failure.
    """
    _validate_subject_id(data)
    _validate_session_plan(data)
    _validate_block_plan(data, word_table=word_table)


