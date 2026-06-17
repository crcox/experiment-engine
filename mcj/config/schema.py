from dataclasses import dataclass

@dataclass(frozen=True)
class SessionConfig:
    num_blocks: int
    show_feedback: bool


