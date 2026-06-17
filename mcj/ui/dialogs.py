from __future__ import annotations

from mcj.runtime.modes import Mode
from mcj.runtime.session_info import SessionInfoProvider, SessionInfo, parse_session_info


class PsychoPyDialogProvider(SessionInfoProvider):
    def get_session_info(self, exp_name: str) -> SessionInfo:
        """
        Prompt the experimenter for session-level information.

        This dialog is shown once at startup and blocks until the user
        confirms or cancels. On cancel, the experiment exits cleanly.

        Args:
            exp_name (str): Name of the experiment (used as dialog title).

        Returns:
            dict: Session information, guaranteed to include required keys.
        """
        from psychopy import gui

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

        return parse_session_info(session_info)


