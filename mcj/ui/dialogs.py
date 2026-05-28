from __future__ import annotations

from psychopy import gui, core
from mcj.config.experiment import ExperimentCondition
from mcj.runtime.exceptions import SessionAbort
from mcj.runtime.end_reasons import SESSION_ABORTED
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionInfo:
    subject_id: int
    condition: ExperimentCondition
    session: int


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
        "condition": [c.value for c in ExperimentCondition],
        "session": "1"
    }

    dlg = gui.DlgFromDict(
        dictionary=ui_info,
        sortKeys=False,
        title=exp_name
    )

    if not dlg.OK:
        raise SessionAbort(reason=SESSION_ABORTED, cause="cancel_button")


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

    try:
        session = int(session_info.get("session", "1"))
    except ValueError:
        raise RuntimeError("session must be an integer")

    condition = ExperimentCondition(
        session_info.get("condition", "").strip()
    )
    if not condition:
        raise RuntimeError("condition is required")

    return SessionInfo(
        subject_id=subject_id,
        condition=condition,
        session=session,
    )
