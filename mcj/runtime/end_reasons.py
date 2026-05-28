from typing import Literal, TypeAlias

TrialEndReason: TypeAlias = Literal["timeout", "aborted", "error", "complete"]
TRIAL_TIMEOUT: TrialEndReason = "timeout"
TRIAL_ABORTED: TrialEndReason = "aborted"
TRIAL_ERROR: TrialEndReason = "error"
TRIAL_COMPLETE: TrialEndReason = "complete"

BlockEndReason: TypeAlias = Literal["aborted", "error", "complete"]
BLOCK_ABORTED: BlockEndReason = "aborted"
BLOCK_ERROR: BlockEndReason = "error"
BLOCK_COMPLETE: BlockEndReason = "complete"

SessionEndReason: TypeAlias = Literal["aborted", "error", "complete"]
SESSION_ABORTED: SessionEndReason = "aborted"
SESSION_ERROR: SessionEndReason = "error"
SESSION_COMPLETE: SessionEndReason = "complete"
