# Conditional Script Events / ScriptConditionEvaluator

## Motivation

The current scripting system is entirely time-based:

```python
.at(4.7).press("0")
.after(1.0).press("space")
```

ScriptScheduler converts a sequence of timestamped ScriptEvents into a stream
of ready events using the authoritative session clock.

This works well for:

- participant responses
- simulated reaction times
- stimulus-driven behavior

However, some scripted actions are not naturally time-based.

For example:

- proceed to next block
- acknowledge an inter-block screen
- respond when a particular experiment state begins
- interact with a task whose progress is determined by synchronization events

These are better expressed as: When X happens, then emit Y.

rather than: At time T, emit Y.

## Design Goal

Introduce conditional script events without:

- adding experiment-state knowledge to ScriptScheduler
- introducing multiple clocks
- violating the "single authoritative session clock" invariant
- coupling scripting directly to task implementations

## Non-Goals

Do not:

- reset script time at block boundaries
- introduce block-relative clocks
- make ScriptScheduler aware of experiment execution
- make adapters responsible for script conditions

The scheduler should remain simple:

session clock
↓
ready ScriptEvents

## Proposed Architecture

### Current

ScriptScheduler
↓
ready ScriptEvents
↓
Input simulation

### Future

ScriptScheduler
↓
candidate ScriptEvents
↓
ScriptConditionEvaluator
↓
ready ScriptEvents
↓
Input simulation

## Responsibilities

### ScriptScheduler

Responsible only for time. It can answer one question:

> Has this event's timestamp arrived?

If no time is specified for the event, it should be emitted immediately and in isolation.

### ScriptConditionEvaluator

Responsible for checking experiment milestones. It can answer questions like:

- Has `wait_for_command` started?
- Has a block begun?
- Has a stimulus appeared?

## Event Model

Potential future shape:

```python
@dataclass(frozen=True)
class ScriptEvent:
    time: float | None
    milestone: ScriptMilestone | None
```

### Invariant:

An event is either:

- time-triggered
- milestone-triggered
- *never both*

## Script Milestones

An explicit vocabulary of lifecycle events.

Example:

```python
class ScriptMilestone(Enum):
    WAIT_FOR_COMMAND_START = auto()
    BLOCK_START = auto()
    PROMPT_START = auto()
    STIMULUS_ONSET = auto()
```

These should correspond to runtime lifecycle events rather than individual task implementations whenever possible.

### Current:

```python
.wait(5.0)
.press("space")
```

### Future:

```python
.when(ScriptMilestone.WAIT_FOR_COMMAND_START)
.press("space")

Meaning: When wait_for_command begins, emit a space key.

### Potential future participant simulation:

```python
.when(ScriptMilestone.STIMULUS_ONSET)
.after(0.7)
.press("0")
```

Meaning: Stimulus appears -> 700 ms reaction time -> Respond

This more closely reflects participant behavior than absolute timestamps.

## Open Questions

### How are milestones emitted?

Possibly:

```python
condition_evaluator.notify(
    ScriptMilestone.WAIT_FOR_COMMAND_START
)
```

from lifecycle functions such as:

```python
wait_for_command()
execute_block()
run_trial()
```

### Should milestones be task-specific or runtime-level?

Preferred: runtime-level

Examples:

```
BLOCK_START
TRIAL_START
WAIT_FOR_COMMAND_START
```

Avoid:

```
CRITERION_JUDGMENT_SPECIFIC_EVENT_X
```

unless there is a compelling reason.

## Rationale

This preserves the current clean separation, Session clock -> ScriptScheduler,
while allowing scripts to react to *experiment state*, without introducing
additional clocks, timeline resets, or scheduler feedback loops.

**The scheduler remains purely temporal.**

The condition evaluator becomes the sole component responsible for state-based
script activation.
