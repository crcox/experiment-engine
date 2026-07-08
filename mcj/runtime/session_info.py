from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence, TypedDict, Any, Type, TypeVar
from dataclasses import dataclass

from mcj.runtime.input import InputMode
from mcj.runtime.tasks import Task
from mcj.runtime.scripting.events import ScriptEvent
from mcj.runtime.environments import Environment
from mcj.runtime.profiles import ExperimentProfile
from mcj.runtime.exceptions import SessionInfoError

EnumType = TypeVar("EnumType", bound=Enum)

class RawSessionInfo(TypedDict, total=False):
    task: str
    environment: str
    profile: str
    input_mode: str
    subject_id: str
    script: Sequence[ScriptEvent] | None
    enable_triggers: bool

def complete_session_info(raw: dict[str, Any]) -> RawSessionInfo:
    return RawSessionInfo(
        task=str(raw["task"]),
        environment=str(raw["environment"]),
        profile=str(raw["profile"]),
        subject_id=str(raw.get("subject_id", "")),
        input_mode=str(raw.get("input_mode", InputMode.REAL.value)),
        script=raw.get("script"),
        enable_triggers=bool(raw.get("enable_triggers", False)),
    )

@dataclass(frozen=True)
class SessionInfo:
    task: Task
    environment: Environment
    profile: ExperimentProfile
    input_mode: InputMode
    subject_id: int | None
    script: Sequence[ScriptEvent] | None
    enable_triggers: bool

class SessionInfoProvider(ABC):

    @abstractmethod
    def get_session_info(self, exp_name: str) -> SessionInfo: ...


def parse_session_info(raw: RawSessionInfo) -> SessionInfo:
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

    def parse_enable_triggers(raw):
        value = raw.get("enable_triggers", False)

        if not isinstance(value, bool):
            raise SessionInfoError(
                "enable_triggers must be a boolean"
            )

        return value

    def parse_enum(
        raw: RawSessionInfo,
        field: str,
        enum_type: Type[EnumType]
    ) -> EnumType:
        value = raw.get(field, "").strip()

        if not value:
            raise SessionInfoError(f"{field} is required")

        try:
            return enum_type(value)
        except ValueError as e:
            raise SessionInfoError(
                f"{value!r} does not correspond to a valid {enum_type.__name__}"
            ) from e

    task = parse_enum(raw, "task", Task)
    environment = parse_enum(raw, "environment", Environment)
    profile = parse_enum(raw, "profile", ExperimentProfile)
    input_mode = parse_enum(raw, "input_mode", InputMode)

    subject_id = parse_subject_id(raw, profile)
    script = parse_script(raw, input_mode)
    enable_triggers = parse_enable_triggers(raw)

    return SessionInfo(
        task=task,
        environment=environment,
        profile=profile,
        subject_id=subject_id,
        input_mode=input_mode,
        script=script,
        enable_triggers=enable_triggers
    )
