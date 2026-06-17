from abc import ABC, abstractmethod
from typing import Any, Sequence
from dataclasses import dataclass

from mcj.runtime.input import InputBackend
from mcj.runtime.scripted import ScriptEvent
from mcj.runtime.modes import Mode
from mcj.runtime.roles import PlanRole
from mcj.runtime.exceptions import SessionInfoError

@dataclass(frozen=True)
class SessionInfo:
    subject_id: int
    mode: Mode
    role: PlanRole
    input_backend: InputBackend
    script: Sequence[ScriptEvent] | None

class SessionInfoProvider(ABC):

    @abstractmethod
    def get_session_info(self, exp_name: str) -> SessionInfo: ...


def parse_session_info(raw: dict[str, Any]) -> SessionInfo:
    try:
        subject_id = int(raw["subject_id"])
    except (KeyError, ValueError):
        raise SessionInfoError("subject_id must be an integer")

    mode_str = raw.get("mode", "").strip()
    if not mode_str:
        raise SessionInfoError("mode is required")

    try:
        mode = Mode(mode_str)
    except ValueError as e:
        raise SessionInfoError(f"{mode_str!r} does not correspond to a valid mode") from e

    role_str = raw.get("role", "").strip()
    if not role_str:
        raise SessionInfoError("role is required")

    try:
        role = PlanRole(role_str)
    except ValueError as e:
        raise SessionInfoError(f"{role_str!r} does not correspond to a valid role") from e

    input_mode_str = raw.get("input_backend", InputBackend.REAL.value).strip()

    try:
        input_backend = InputBackend(input_mode_str)
    except ValueError as e:
        raise SessionInfoError(f"{input_mode_str!r} does not correspond to a valid input mode") from e

    script = raw.get("script")
    if input_backend == InputBackend.SCRIPTED:
        if script is None:
            raise SessionInfoError(f"input_backend=={InputBackend.SCRIPTED}, but no 'script' was provided. This is a misconfiguration.")
    else:
        if script is not None:
            raise SessionInfoError(f"input_backend!={InputBackend.SCRIPTED}, but a 'script' was provided. This is a misconfiguration.")

    if script is not None:
        if not isinstance(script, Sequence):
            raise SessionInfoError("script must be a sequence of ScriptEvent")

        if not all(isinstance(e, ScriptEvent) for e in script):
            raise SessionInfoError("script must contain only ScriptEvent objects")

    return SessionInfo(
        subject_id=subject_id,
        mode=mode,
        role=role,
        input_backend=input_backend,
        script=script
    )
