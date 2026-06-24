from mcj.runtime.end_reasons import EndReason

class ExperimentAbort(Exception):
    """Raised to abort the experiment for a known semantic reason."""
    def __init__(
        self,
        *,
        reason: EndReason,
        cause: str,
        message: str | None = None
    ):
        super().__init__(message)
        self.reason = reason 
        self.cause = cause 
        self.message = message

class EscapePressed(ExperimentAbort):
    """Raised when the user presses Escape to abort the session."""
    def __init__(self):
        super().__init__(
            reason=EndReason.ABORTED,
            cause="escape_key",
            message="Experiment aborted (escape key pressed)"
        )

class CedrusAlignmentTimout(ExperimentAbort):
    """Raised when the user presses Escape to abort the session."""
    def __init__(self):
        super().__init__(
            reason=EndReason.TIMEOUT,
            cause="cedrus_alignment",
            message="Cedrus alignment timed out"
        )

class CancelPressed(ExperimentAbort):
    """Raised when the user presses Cancel in dialog box to abort the session."""
    def __init__(self):
        super().__init__(
            reason=EndReason.ABORTED,
            cause="cancel_dialog",
            message="Experiment cancelled by user"
        )

class DataContractError(ExperimentAbort):
    """Raised when an asset or input file violates expected schema"""
    def __init__(self, message: str | None = None):
        super().__init__(
            reason=EndReason.INVALID_INPUT,
            cause="invalid_file",
            message=message or "Invalid data encountered in input file"
        )

class CriterionJudgmentPlanError(Exception):
    """Raised when a trial plan file is malformed or invalid."""

class SessionInfoError(ExperimentAbort):
    """Raised when input to the session info dialog violates expected schema"""
    def __init__(self, message: str | None = None):
        super().__init__(
            reason = EndReason.INVALID_INPUT,
            cause = "invalid_session_info",
            message = message or "Invaid session info was provided"
        )


