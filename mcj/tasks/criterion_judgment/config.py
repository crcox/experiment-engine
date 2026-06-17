from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CriterionJudgmentTaskConfig:
    instructions_path: Path
