from pathlib import Path
from mcj.runtime.modes import Mode
import sys

class _Paths:
    def __init__(self) -> None:
        self._root: Path | None = None
        self._subject_id: int | None = None
        self._mode: Mode | None = None

    def initialize(self, root: Path, subject_id: int, mode: Mode) -> None:
        self._root = root
        self._subject_id = subject_id
        self._mode = mode

    def _require_root(self) -> Path:
        if self._root is None:
            raise RuntimeError("paths.initialize(root, subject_id, mode) must be called first")
        return self._root

    def _require_subject_id(self) -> int:
        if self._subject_id is None:
            raise RuntimeError("paths.initialize(root, subject_id, mode) must be called first")
        return self._subject_id

    def _require_mode(self) -> Mode:
        if self._mode is None:
            raise RuntimeError("paths.initialize(root, subject_id, mode) must be called first")
        return self._mode


    @property
    def _subject_code(self) -> str:
        return "subj-{i:03d}".format(i=self._require_subject_id())

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
    def SESSION_PLAN(self) -> Path:
        subject_code = self._subject_code
        mode = self._require_mode()
        if mode == Mode.PRACTICE:
            return self.ASSETS / "practice" / "practice.json"
        else:
            return self.ASSETS / "subjects" / f"{subject_code}.json"

    @property
    def PRACTICE_PLAN(self) -> Path:
        return self.ASSETS / "practice.json"

    @property
    def DATA(self) -> Path:
        return self.ROOT / "data" / self._subject_code

    @property
    def EXTERNAL(self) -> Path:
        return self.ROOT / "external"

    @property
    def FTD2XX(self) -> Path:
        arch = "x64" if sys.maxsize > 2**32 else "i386"
        return self.EXTERNAL / "ftd2xx" / arch


paths = _Paths()
