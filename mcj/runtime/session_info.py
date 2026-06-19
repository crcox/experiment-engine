from abc import ABC, abstractmethod
from typing import Any, Sequence
from dataclasses import dataclass

from mcj.runtime.input import InputBackend
from mcj.runtime.scripted import ScriptEvent
from mcj.runtime.environments import Environment
from mcj.runtime.profiles import TaskProfile
from mcj.runtime.exceptions import SessionInfoError

@dataclass(frozen=True)
class SessionInfo:
    subject_id: int
    environment: Environment
    task_profile: TaskProfile
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

    environment_str = raw.get("environment", "").strip()
    if not environment_str:
        raise SessionInfoError("environment is required")

    try:
        environment = Environment(environment_str)
    except ValueError as e:
        raise SessionInfoError(f"{environment_str!r} does not correspond to a valid environment") from e

    profile_str = raw.get("profile", "").strip()
    if not profile_str:
        raise SessionInfoError("profile is required")

    try:
        profile = TaskProfile(profile_str)
    except ValueError as e:
        raise SessionInfoError(f"{profile_str!r} does not correspond to a valid profile") from e

    input_backend_str = raw.get("input_backend", InputBackend.REAL.value).strip()

    try:
        input_backend = InputBackend(input_backend_str)
    except ValueError as e:
        raise SessionInfoError(f"{input_backend_str!r} does not correspond to a valid input environment") from e

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
        environment=environment,
        task_profile=profile,
        input_backend=input_backend,
        script=script
    )
