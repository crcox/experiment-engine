from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class TaskAssetPaths:
    task_root: Path
    base: Path
    profile: Path
