from dataclasses import dataclass

@dataclass(frozen=True)
class InstructionSlide:
    id: str
    title: str
    body: str


@dataclass(frozen=True)
class InstructionDocument:
    slides: list[InstructionSlide]
