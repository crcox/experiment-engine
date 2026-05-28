from dataclasses import dataclass
from typing import Literal

ConfigName = Literal["practice", "experimental"]
TaskCode = Literal["mcj_domain", "mcj_size", "mcj_mcj_danger", "mcj_orthography"]

@dataclass(frozen=True)
class FeedbackConfig:
    duration_seconds: float | None
    color_positive: str | None
    color_negative: str | None
    color_neutral: str | None

@dataclass(frozen=True)
class TrialModeConfig:
    name: ConfigName
    task_code: TaskCode
    trial_duration_seconds: float | None
    block_duration_seconds: float | None
    feedback: FeedbackConfig | None

    @property
    def provide_feedback(self) -> bool:
        return self.feedback is not None

