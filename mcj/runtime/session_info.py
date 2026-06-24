from abc import ABC, abstractmethod
from typing import Any, Sequence
from dataclasses import dataclass

from mcj.runtime.input import InputMode
from mcj.runtime.scripting.events import ScriptEvent
from mcj.runtime.environments import Environment
from mcj.runtime.profiles import TaskProfile
from mcj.runtime.exceptions import SessionInfoError

@dataclass(frozen=True)
class SessionInfo:
    subject_id: int
    environment: Environment
    task_profile: TaskProfile
    input_mode: InputMode
    script: Sequence[ScriptEvent] | None
    enable_triggers: bool = False

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

    input_mode_str = raw.get("input_mode", InputMode.REAL.value).strip()

    try:
        input_mode = InputMode(input_mode_str)
    except ValueError as e:
        raise SessionInfoError(f"{input_mode_str!r} does not correspond to a valid input environment") from e

    INPUT_MODE_CAPABILITIES = {
        InputMode.SCRIPTED: {"reads_script": True, },
        InputMode.SIMULATED: {"reads_script": True, },
        InputMode.REAL: {"reads_script": False, },
    }
    capabilities = INPUT_MODE_CAPABILITIES[input_mode]

    script = raw.get("script")
    if capabilities["reads_script"] and script is None:
        raise SessionInfoError(f"The input_mode {input_mode} requires a script")

    if script is not None and not capabilities["reads_script"]:
        raise SessionInfoError(f"The input_mode {input_mode} does not support scripts")

    if script is not None:
        if not isinstance(script, Sequence):
            raise SessionInfoError("script must be a sequence of ScriptEvent")

        if not all(isinstance(e, ScriptEvent) for e in script):
            raise SessionInfoError("script must contain only ScriptEvent objects")

    return SessionInfo(
        subject_id=subject_id,
        environment=environment,
        task_profile=profile,
        input_mode=input_mode,
        script=script,
    )
