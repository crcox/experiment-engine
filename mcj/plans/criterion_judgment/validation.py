from __future__ import annotations

from typing import Any
from mcj.runtime.exceptions import CriterionJudgmentPlanError
from mcj.plans.criterion_judgment.schema import CriterionJudgmentCondition
from mcj.stimuli.schema import WORDS


def _validate_subject_id(data: dict[str, Any]) -> None:
    subject_id = data["subject_id"]
    if not isinstance(subject_id, int):
        raise CriterionJudgmentPlanError("`subject_id` must be an integer; got {type(subject_id).__name__}")


def _validate_condition(data: dict[str, Any]) -> None:
    condition = data["condition"]
    if not isinstance(condition, str):
        raise CriterionJudgmentPlanError("`condition` must be a string; got {type(condition).__name__}")

    CriterionJudgmentCondition(condition)


def _validate_word_sequence(
    word_sequence: list[Word],
    *,
    context: str
) -> None:
    valid_nodes = set(range(len(IMAGE_NAMES)))
    seq_nodes = set(node_sequence)

    invalid_nodes = seq_nodes - valid_nodes
    if invalid_nodes:
        raise SequenceMTSPlanError(
            f"`{context}` contains invalid node indices: "
            f"{sorted(invalid_nodes)}"
        )

def _validate_sequence_mts_trial_spec(data: dict[str, Any]) -> None:
    required_keys = {
        "subject_id",
        "condition",
        "image_by_node",
        "node_sequence",
        "blocks",
    }

    missing = required_keys - data.keys()
    if missing:
        raise SequenceMTSPlanError(
            f"SessionPlan is missing required keys: {sorted(missing)}"
        )

    image_by_node = data["image_by_node"]
    if not isinstance(image_by_node, list):
        raise SequenceMTSPlanError("`image_by_node` must be a list[str]; got {type(image_by_node).__name__}")

    for i,value in enumerate(image_by_node):
        if not isinstance(value, str):
            raise SequenceMTSPlanError(
                f"`image_by_node[{i:d}]` must be a string; got {type(value).__name__}"
            )

    node_sequence = data["node_sequence"]
    if not isinstance(node_sequence, list):
        raise SequenceMTSPlanError("`node_sequence` must be a list[int]")

    if not all(isinstance(x, int) for x in node_sequence):
        raise SequenceMTSPlanError("`node_sequence` must contain only integers")

    _validate_image_names(image_by_node, context="image_by_node")
    _validate_node_sequence(node_sequence, context="node_sequence")


def _validate_sequence_mts_block_plan(data: dict[str, Any]) -> None:
    blocks = data["blocks"]
    if not isinstance(blocks, list):
        raise SequenceMTSPlanError("`blocks` must be a list[dict[str, list[str]]]")

    for block in blocks:
        if not isinstance(block, dict):
            raise SequenceMTSPlanError("Each `block` must be a dict[str, list[str]]")

        if "image_by_ring_slot" not in block:
            raise SequenceMTSPlanError("Each `block` dict must have key 'image_by_ring_slot'")

        if not isinstance(block["image_by_ring_slot"], list):
            raise SequenceMTSPlanError("`block['image_by_ring_slot']` must be list[str]")

        if not all(isinstance(x, str) for x in block["image_by_ring_slot"]):
            raise SequenceMTSPlanError("`block['image_by_ring_slot']` must be list[str]")

    for i,block in enumerate(blocks):
        _validate_image_names(block["image_by_ring_slot"], context=f"block[{i}]")


def validate_sequence_mts_plan(data: dict[str, Any]) -> None:
    """
    Validate the structure and contents of a session plan dictionary.

    Raises:
        SequenceMTSPlanError on first failure.
    """
    _validate_subject_id(data)
    _validate_condition(data)
    _validate_sequence_mts_trial_spec(data)
    _validate_sequence_mts_block_plan(data)


