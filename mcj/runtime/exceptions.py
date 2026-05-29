from mcj.runtime.end_reasons import SESSION_ABORTED, INVALID_INPUT, SessionEndReason

class ExperimentAbort(Exception):
    """Raised to abort the experiment for a known semantic reason."""
    reason: SessionEndReason
    cause: str

class EscapePressed(ExperimentAbort):
    """Raised when the user presses Escape to abort the session."""
    def __init__(self):
        self.reason = SESSION_ABORTED
        self.cause = "escape_key"
        super().__init__()

class CancelPressed(ExperimentAbort):
    """Raised when the user presses Cancel in dialog box to abort the session."""
    def __init__(self):
        self.reason = SESSION_ABORTED
        self.cause = "cancel_dialog"
        super().__init__()

class DataContractError(ExperimentAbort):
    """Raised to abort the experiment when an asset is invalid"""
    def __init__(self):
        self.reason = INVALID_INPUT
        self.cause = "invalid_file"
        super().__init__()

class CriterionJudgmentPlanError(Exception):
    """Raised when a trial plan file is malformed or invalid."""

class SessionInfoError(ExperimentAbort):
    """Raised to abort the experiment when session info is invalid"""
    def __init__(self):
        self.reason = INVALID_INPUT
        self.cause = "invalid_session_info"
        super().__init__()


