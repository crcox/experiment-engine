from __future__ import annotations

from psychopy import gui
from mcj.runtime.modes import Mode
from mcj.runtime.roles import PlanRole
from mcj.runtime.exceptions import CancelPressed, SessionInfoError
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionInfo:
    subject_id: int
    mode: Mode
    role: PlanRole


def get_session_info(exp_name: str) -> SessionInfo:
    """
    Prompt the experimenter for session-level information.

    This dialog is shown once at startup and blocks until the user
    confirms or cancels. On cancel, the experiment exits cleanly.

    Args:
        exp_name (str): Name of the experiment (used as dialog title).

    Returns:
        dict: Session information, guaranteed to include required keys.
    """

    # Lists of strings are presented as a drop-down menu of options in the
    # dialog box
    ui_info: dict[str, str | list[str]] = {
        "subject_id": "",
        "mode": [m.value for m in Mode]
    }

    dlg = gui.DlgFromDict(
        dictionary=ui_info,
        sortKeys=False,
        title=exp_name
    )

    if not dlg.OK:
        raise CancelPressed


    session_info: dict[str, str] = {
        key: value
        for key, value in ui_info.items()
        if isinstance(value, str)
    }

    return _parse_session_info(session_info)


def _parse_session_info(session_info: dict[str, str]) -> SessionInfo:
    try:
        subject_id = int(session_info["subject_id"])
    except (KeyError, ValueError):
        raise RuntimeError("subject_id must be an integer")

    mode_str = session_info.get("condition", "").strip()
    if not mode_str:
        raise RuntimeError("condition is required")

    try:
        mode = Mode(mode_str)
    except ValueError as e:
        raise SessionInfoError from e

    if mode == Mode.PRACTICE:
        role = PlanRole.PRACTICE
    elif mode == Mode.SCANNER:
        role = PlanRole.MAIN

    return SessionInfo(
        subject_id=subject_id,
        mode=mode,
        role=role
    )
