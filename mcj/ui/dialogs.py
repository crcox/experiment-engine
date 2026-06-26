from __future__ import annotations

from mcj.runtime.exceptions import CancelPressed
from mcj.runtime.environments import Environment
from mcj.runtime.input import InputMode
from mcj.runtime.profiles import ExperimentProfile
from mcj.runtime.session_info import SessionInfoProvider, SessionInfo, complete_session_info, parse_session_info

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
        ui_info = {
            "environment": [e.value for e in Environment],
            "profile": [p.value for p in ExperimentProfile],
            "subject_id": "",
        }

        dlg = gui.DlgFromDict(
            dictionary=ui_info,
            sortKeys=False,
            title=exp_name
        )

        if not dlg.OK:
            raise CancelPressed

        if not "input_mode" in ui_info:
            ui_info["input_mode"] = InputMode.REAL.value
            ui_info["script"] = None


        session_info_raw = complete_session_info(ui_info)

        return parse_session_info(session_info_raw)


