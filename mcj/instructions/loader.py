from __future__ import annotations

from mcj.instructions.schema import InstructionDocument
import yaml

def load_instructions(path) -> InstructionDocument:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Instruction file must contain a list of slides")

    for i, slide in enumerate(data["slides"]):
        if "title" not in slide or "body" not in slide:
            raise ValueError(f"Slide {i} must have 'title' and 'body'")
        if not isinstance(slide["title"], str):
            raise TypeError(f"Slide {i} 'title' must be a string")
        if not isinstance(slide["body"], str):
            raise TypeError(f"Slide {i} 'body' must be a string")

    return data
