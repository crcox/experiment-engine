import sys
from pathlib import Path

from mcj.runtime.tasks import Task
from mcj.runtime.setup_types import TaskAssetPaths
from mcj.runtime.profiles import ExperimentProfile
from mcj.runtime.ids import make_subject_code

class _Paths:
    def __init__(self) -> None:
        self._root: Path | None = None

    def initialize(self, root: Path) -> None:
        self._root = root

    def _require_root(self) -> Path:
        if self._root is None:
            raise RuntimeError("paths.initialize(root) must be called first")
        return self._root

    @property
    def ROOT(self) -> Path:
        return self._require_root()

    @property
    def ASSETS(self) -> Path:
        return self.ROOT / "assets" 

    @property
    def WORDS_CSV(self) -> Path:
        return self.ASSETS / "words-experiment-all.csv"

    @property
    def INSTRUCTIONS(self) -> Path:
        return self.ASSETS / "instructions"

    @property
    def DATA(self) -> Path:
        return self.ROOT / "data"

    @property
    def EXTERNAL(self) -> Path:
        return self.ROOT / "external"

    @property
    def FTD2XX(self) -> Path:
        arch = "x64" if sys.maxsize > 2**32 else "i386"
        return self.EXTERNAL / "ftd2xx" / arch

    def asset_paths_for_profile(
        self,
        task: Task,
        profile: ExperimentProfile
    ) -> TaskAssetPaths:
        return TaskAssetPaths(
            task_root=self.ASSETS / task.value,
            base=self.ASSETS / task.value / "base",
            profile=self.ASSETS / task.value / profile.value,
        )

    def data_dir_for_profile(self, task: Task, profile: ExperimentProfile, subject_id: int | None) -> Path:
        base = self.DATA / task.value / profile.value

        if profile.requires_subject_id:
            assert subject_id is not None
            return base / make_subject_code(subject_id)

        else:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            return base / ts

paths = _Paths()
