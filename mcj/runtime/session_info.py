from abc import ABC, abstractmethod
from typing import Sequence, TypedDict, Any
from dataclasses import dataclass

from mcj.runtime.input import InputMode
from mcj.runtime.tasks import Task
from mcj.runtime.scripting.events import ScriptEvent
from mcj.runtime.environments import Environment
from mcj.runtime.profiles import ExperimentProfile
from mcj.runtime.exceptions import SessionInfoError

class RawSessionInfo(TypedDict, total=False):
    environment: str
    profile: str
    subject_id: str
    input_mode: str
    script: Sequence[ScriptEvent] | None

def complete_session_info(raw: dict[str, Any]) -> RawSessionInfo:
    return RawSessionInfo(
        environment=str(raw["environment"]),
        profile=str(raw["profile"]),
        subject_id=str(raw["subject_id"]),
        input_mode=str(raw.get("input_mode", InputMode.REAL.value)),
        script=raw.get("script"),
    )

@dataclass(frozen=True)
class SessionInfo:
    task: Task
    environment: Environment
    profile: ExperimentProfile
    subject_id: int | None
    input_mode: InputMode
    script: Sequence[ScriptEvent] | None
    enable_triggers: bool = False

class SessionInfoProvider(ABC):

    @abstractmethod
    def get_session_info(self, exp_name: str) -> SessionInfo: ...


def parse_session_info(raw: RawSessionInfo) -> SessionInfo:
    def parse_task(raw: RawSessionInfo) -> Task:
        task_str = raw.get("task", "").strip()
        if not task_str:
            raise SessionInfoError("task is required")

        try:
            return Task(task_str)
        except ValueError as e:
            raise SessionInfoError(f"{task_str!r} does not correspond to a valid task") from e

    def parse_environment(raw: RawSessionInfo) -> Environment:
        environment_str = raw.get("environment", "").strip()
        if not environment_str:
            raise SessionInfoError("environment is required")

        try:
            return Environment(environment_str)
        except ValueError as e:
            raise SessionInfoError(f"{environment_str!r} does not correspond to a valid environment") from e

    def parse_task_profile(raw: RawSessionInfo) -> ExperimentProfile:
        task_profile_str = raw.get("profile", "").strip()
        if not task_profile_str:
            raise SessionInfoError("profile is required")

        try:
            return ExperimentProfile(task_profile_str)
        except ValueError as e:
            raise SessionInfoError(f"{task_profile_str!r} does not correspond to a valid ExperimentProfile") from e

    def parse_subject_id(raw: RawSessionInfo, profile: ExperimentProfile) -> int | None:
        subject_id_str = raw.get("subject_id", "").strip()
        if not subject_id_str:
            if profile.requires_subject_id:
                raise SessionInfoError(f"Subject ID is required for {profile} profile")
            else:
                return None

        try:
            return int(subject_id_str)
        except (ValueError) as e:
            raise SessionInfoError("subject_id must be an integer") from e

    def parse_input_mode(raw: RawSessionInfo) -> InputMode:
        input_mode_str = raw.get("input_mode", InputMode.REAL.value).strip()

        try:
            return InputMode(input_mode_str)
        except ValueError as e:
            raise SessionInfoError(f"{input_mode_str!r} does not correspond to a valid input mode") from e

    def parse_script(raw: RawSessionInfo, input_mode: InputMode) -> Sequence[ScriptEvent] | None:
        script = raw.get("script")
        if script is None and input_mode.requires_script:
            raise SessionInfoError(f"The input_mode {input_mode} requires a script")

        if script is not None and not input_mode.requires_script:
            raise SessionInfoError(f"The input_mode {input_mode} does not support scripts")

        if script is not None:
            if not isinstance(script, Sequence):
                raise SessionInfoError("script must be a sequence of ScriptEvent")

            if not all(isinstance(e, ScriptEvent) for e in script):
                raise SessionInfoError("script must contain only ScriptEvent objects")

        return script

    task = parse_task(raw)
    environment = parse_environment(raw)
    profile = parse_task_profile(raw)
    subject_id = parse_subject_id(raw, profile)
    input_mode = parse_input_mode(raw)
    script = parse_script(raw, input_mode)

    return SessionInfo(
        task=task,
        environment=environment,
        profile=profile,
        subject_id=subject_id,
        input_mode=input_mode,
        script=script,
    )
