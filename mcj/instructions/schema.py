from typing import TypedDict


class InstructionSlide(TypedDict):
    title: str
    body: str


class InstructionDocument(TypedDict):
    slides: list[InstructionSlide]
