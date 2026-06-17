from __future__ import annotations

import yaml
from typing import Sequence
from pathlib import Path

from mcj.instructions.schema import InstructionSlide
from mcj.runtime.exceptions import DataContractError

def load_instructions(path: Path) -> Sequence[InstructionSlide]:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise DataContractError("Instruction file must contain a top-level mapping")

    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Instruction file must contain a list of slides")

    required_fields = {"id", "title", "body"}
    slides = []
    for i, slide in enumerate(data["slides"]):
        missing = required_fields - set(slide.keys())
        if missing:
            raise DataContractError(
                f"Slide {i} is missing required fields:" +
                "\n".join(f"  {m!r}" for m in missing)
            )
        if not isinstance(slide["id"], str):
            raise DataContractError(f"Slide {i} 'id' must be a string")
        if not isinstance(slide["title"], str):
            raise DataContractError(f"Slide {i} 'title' must be a string")
        if not isinstance(slide["body"], str):
            raise DataContractError(f"Slide {i} 'body' must be a string")

        slides.append(InstructionSlide(
            id=slide['id'],
            title=slide['title'],
            body=slide['body']
        ))

    return slides
