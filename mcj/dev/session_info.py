import json
from pathlib import Path
from typing import Any
from mcj.runtime.session_info import SessionInfoProvider, SessionInfo, parse_session_info

class StaticSessionInfoProvider(SessionInfoProvider):

    def __init__(self, session_info_dict: dict[str, Any]):
        self._session_info_dict = session_info_dict

    def get_session_info(self, exp_name: str) -> SessionInfo:
        return parse_session_info(self._session_info_dict)


class JSONSessionInfoProvider(SessionInfoProvider):

    def __init__(self, path: Path):
        self._path = path

    def get_session_info(self, exp_name: str) -> SessionInfo:
        with open(self._path, encoding="utf-8") as f:
            data = json.load(f)

        return parse_session_info(data)
