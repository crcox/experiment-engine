import json
from pathlib import Path
from mcj.runtime.session_info import (
        SessionInfoProvider,
        RawSessionInfo,
        SessionInfo,
        parse_session_info,
    )

class StaticSessionInfoProvider(SessionInfoProvider):

    def __init__(self, session_info_raw: RawSessionInfo):
        self._session_info_raw = session_info_raw

    def get_session_info(self, exp_name: str) -> SessionInfo:
        _ = exp_name
        return parse_session_info(self._session_info_raw)


class JSONSessionInfoProvider(SessionInfoProvider):

    def __init__(self, path: Path):
        self._path = path

    def get_session_info(self, exp_name: str) -> SessionInfo:
        _ = exp_name
        with open(self._path, encoding="utf-8") as f:
            data = json.load(f)

        return parse_session_info(data)
