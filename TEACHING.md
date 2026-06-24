# Teaching

The end goal is for this experiment to evolve into a teaching tool and
framework-by-example for future experiment design in my lab. This is a
collection of notes and thoughts that may be turned into teaching materials
down the line. Much of what is in this document is M365 Copilot generated.

## The simple story

1. main.py starts the experiment
2. The config decides what to run
3. A task runs (instructions → trials)
4. Each routine uses actions + mappings
5. The runtime handles input, timing, and events
6. Adapters connect everything to real hardware


## Student diagram

You write tasks. The framework handles everything else.

   ┌────────────────────────────┐
   │       TASK (your code)     │
   │  - instructions            │
   │  - trials                  │
   └────────────┬───────────────┘
                ↓ uses

   ┌────────────────────────────┐
   │     RUNTIME ENGINE         │
   │  - states                  │
   │  - actions                 │
   │  - mappings                │
   │  - timing                  │
   └────────────┬───────────────┘
                ↓ relies on

   ┌────────────────────────────┐
   │   SESSION + EXECUTION      │
   │  - inputs                  │
   │  - mode (practice/main)    │
   │  - config                  │
   └────────────┬───────────────┘
                ↓ connected via

   ┌────────────────────────────┐
   │        ADAPTERS            │
   │  - keyboard                │
   │  - cedrus box              │
   │  - psychopy display        │
   └────────────────────────────┘


## Diagram for documentation

 main.py
    ↓
 config/experiment.py   ← chooses role (practice/main/dev/...)
    ↓
 task.run()
    ↓
 ┌────────────────────────────┐
 │   ROUTINES                 │
 │ - present_instructions()   │
 │ - run_trial()              │
 └────────────┬───────────────┘
              ↓
 ┌─────────────────────────────┐
 │   EXECUTION CONTEXT         │
 │  ExecutionContext[ActionT]  │
 └────────────┬────────────────┘
              ↓
 ┌─────────────────────────────┐
 │   ROLE CONFIG               │
 │  TaskProfileConfig[ActionT]        │
 │   - mappings                │
 │   - termination             │
 └────────────┬────────────────┘
              ↓
 ┌─────────────────────────────┐
 │   RUNTIME CORE              │
 │  events → actions → states  │
 └────────────┬────────────────┘
              ↓
 ┌─────────────────────────────┐
 │   SESSION RUNTIME           │
 │  (input, mode, timing)      │
 └────────────┬────────────────┘
              ↓
        ADAPTERS (hardware)


# How to add a new task (v1)

A task is instructions + trials + configuration

---

## Step 1. Define your vocabulary of actions tailored to your task

Action represent *meaning*, not key presses. These are nothing more than
symbollic representations.

📁 `tasks/my_task/actions.py`

```python
from enum import Enum

class MyAction(Enum):
    LEFT = "left"
    RIGHT = "right"
    ADVANCE = "advance"
```

---

## Step 2. Define your mapping from input to action

📁 `tasks/my_task/mapping.py`

```python
from mcj.runtime.mapping import ActionMapping
from mcj.runtime.session import SessionRuntime

from mcj.tasks.my_task.actions import MyAction

def build_action_mapping(session: SessionRuntime) -> ActionMapping[MyAction]:
    return ActionMapping({
        "f": MyAction.LEFT,
        "j": MyAction.RIGHT,
    })
```

---

## Step 3. Create your TaskProfileConfig

TaskProfileConfig defines how your task behaves.

📁 `tasks/my_task/config.py`

```python
from mcj.runtime.roles import TaskProfileConfig
from mcj.runtime.mapping import key_mapping, dynamic_mapping
from mcj.runtime.termination import ActionTermination, ActionOrTimeoutTermination

from mcj.tasks.my_task.actions import MyAction
from mcj.tasks.my_task.mapping import build_action_mapping

def build_task_config():
    return TaskProfileConfig[MyAction](
        termination_by_state={
            # example
            "PROMPT": ActionTermination(),
            "STIMULUS": ActionOrTimeoutTermination(),
        },
        action_mapping_by_state={
            # simple mapping
            "PROMPT": key_mapping({"space": MyAction.ADVANCE}),

            # dynamic mapping
            "STIMULUS": dynamic_mapping(build_action_mapping),
        },
    )
```

## Step 4. Impement your task logic

For simple tasks, everything might be managed my one trial loop. 

📁 `tasks/my_task/task.py`

```python
from mcj.routines.instructions.instructions import present_instructions
from mcj.runtime.execution import ExecutionContext

def run(factory, instruction_ctx, task_ctx, run_cfg):
    present_instructions(factory, ..., instruction_ctx)

    # your trial loop here
```

## Step 5. Add it to the experiment config

📁 `config/experiment.py`

```python
CONFIG_BY_ROLE = {
    PlanRole.PRACTICE: {
        "instructions": build_instruction_config(),
        "task": build_my_task_config(),
    },
}
```

---

# Things missing from the walkthrough above

* How to add instructions, and how to differentiate experiment-level from
  task-level instructions.

* Step 4 may lead students to try to write their whole task in one file, while
  a typical task will probably have a structure more like:

  > `run()` -> [`present_*()`, `run_block()` -> `run_trial()]`

  This is more complicated, but I think will do a lot to orient students to
  practical design patterns.

* There is no mention of defining states, and the TaskProfileConfig appears to be
  keyed with strings rather than enums. Again, this may be a useful
  simplification in a first-blush presentation... but it will be very confusing
  if a student takes it literally and jumps in to building.

* There is no mention of emitters--their experiment will not record any events!

* Similarly, there is no mention of the event record, logging, etc. This
  event-driven design is going to be different from what students are used to,
  and will require a decent amount of explanation.

* It goes without saying that the way flow control is handled within a trial
  loop needs to be explicitly taught and demonstrated at some point, maybe not
  right off the bat, but early in the teaching materials I think.

* I think it is critical to present early an often to students that they should
  develop in layers, and the framework deliberately faciliates this. By this, I
  mean they should not rush to see their experiment visually rendering text and
  images. This is going to be a **big** paradigm shift for students. The
  typical workflow is do a bit of configuration in a builder, literally run the
  experiment as if you were a participant to see how it all plays out, and
  iterate (very slowly) until it looks and behaves correctly. Students should
  understand the behavior can be assessed, in large part, independently of
  visual (or auditory) presentation. They should learn to test their flow
  control with scripts, confirm that their events are being emitted and logged
  correctly, and only then plug into the PsychoPy adapter to dial in their
  stimuli (and when doing that, they should understand that they can easily set
  up a `dev` role with fewer blocks, fewer trials, shorter durations, etc. to
  make this phase of development more efficient, without needing to modify
  their confirmed-working configuration of the full task behavior.

* On the topic of roles, it should be made clear to students what roles are and
  that "practice" and "main" are just differently configured passes over the
  same code.

---

# How to add a new task (v2)

A task is a structured system, not a single function.

A task is typically structured as follows. This pattern is *intentional*, and
will emerge in most tasks.

```
run()
  ↓
present_*()
run_block()
  ↓
run_trial()
```

---

## Step 1. Define your vocabulary of actions tailored to your task

Action represent *meaning*, not key presses. These are nothing more than
symbollic representations.

📁 `tasks/my_task/actions.py`

```python
from enum import Enum

class MyAction(Enum):
    LEFT = "left"
    RIGHT = "right"
    ADVANCE = "advance"
```

## Step 2. Define states that can occur during your task

This corresponds to the structure of your task.

📁 `tasks/my_task/states.py`

```python
from enum import Enum, auto

class MyState(Enum):
    FIXATION = auto()
    STIMULUS = auto()
    FEEDBACK = auto()
```

---

## Step 3. Define your mapping from input to action

Inputs map to actions, which are different from responses, and are not yet
behaviors. When a participant presses a key or a button, this is associated
with a device-level event. Only some events are attended to by the experiment,
and only some attended events are interpretted as actions. Whether an event is
interpretted as an action depends on the state of the task/experiment. Actions
are then interpretted. An action might be a task-relevant response, it may
signal that the display should change, it might mean that you should advance to
a new instruction screen, etc. But these `behaviors` are defined later, after
interpretting an `action`. 


📁 `tasks/my_task/mapping.py`

```python
from mcj.runtime.mapping import ActionMapping
from mcj.runtime.session import SessionRuntime

from mcj.tasks.my_task.actions import MyAction

def build_action_mapping(session: SessionRuntime) -> ActionMapping[MyAction]:
    return ActionMapping({
        "f": MyAction.LEFT,
        "j": MyAction.RIGHT,
    })
```

---

## Step 4. Create your TaskProfileConfig

TaskProfileConfig defines how your task behaves. Notice that behavior is defined for
each state. This means that behavior is state-dependent.

Notice how enums are being used here. The TaskProfileConfig needs to know about your
action vocabulary `MyAction`, and states are refering to `MyState` enum
members. This has many consequences, but one is that your states are *your
states*. Even if `FIXATION` is a state in every task, `MyState.FIXATION` is
yours and the experiment code will never confuse it for any other fixation
state. The cleanly separates configured behavior by state, where each task has
a bespoke state space.

📁 `tasks/my_task/config.py`

```python
from mcj.runtime.roles import TaskProfileConfig
from mcj.runtime.mapping import key_mapping, dynamic_mapping
from mcj.runtime.termination import ActionTermination, ActionOrTimeoutTermination

from mcj.tasks.my_task.actions import MyAction
from mcj.tasks.my_task.states import MyState
from mcj.tasks.my_task.mapping import build_action_mapping

def build_task_config():
    return TaskProfileConfig[MyAction](
        termination_by_state={
            # example
            MyState.PROMPT: ActionTermination(),
            MyState.STIMULUS: ActionOrTimeoutTermination(),
        },
        action_mapping_by_state={
            # simple mapping
            MyState.PROMPT: key_mapping({"space": MyAction.ADVANCE}),

            # dynamic mapping
            MyState.STIMULUS: dynamic_mapping(build_action_mapping),
        },
    )
```

---

## Step 5. Build the task structure

Tasks are composed, not written in one file, and each level has clear
responsibilities. The top level function, `run()`, is responsibible for
orchestrating all the routines within the task, including looping over blocks.

The `run_block()` function is responsible for providing whatever is needed to
correctly run each trial in the block. For example, if running an experiment
where trial and state transitions need to be synchronized with a measurement
device (e.g., an MRI machine), `run_block()` will generate the schedule
dictating when each state will begin and end for the whole block.

The `run_trial()` function is resposible for the trial logic.

📁 `tasks/my_task/task.py`

```python
def run(...):
    present_instructions(...)
    for block in ...:
        run_block(...)

```

📁 `tasks/my_task/block.py`

```python
def run_block(...):
    run_trial(...)

```

📁 `tasks/my_task/trial.py`

```python
def run_trial(...):
    # core loop

```

---

## Step 6. Instruction handling

There is a top-level instruction routine (defined in `routine/instructions`)
that can be shared across tasks. It is very simple: it take a title and a
single block of body text. If you want to write your own instruction routines,
these can be simply adapted from this template. Copy-paste the instruction.py
routine into your task directory and adapt as needed.

# TODO: EXAMPLE

---

## Step 7. Emitters

A key concept in this experiment design framework is that *events* are
*emitted* to and *recorded* by the *event stream* so that they can be *logged*.
This is the single mechanistic flow for capturing data during the experiment.

An event may be the setting of a configuration, the beginning or end of a
session/task/block/trial, the receipt of an event, the comprehension of an
action, the recording of a response, or anything else of note.

If you do not emit events, you have not collected data!

There are many generic emitters that are defined in `runtime/emitters.py`, but
you will need to write your own to capture data relevant to your task. Emitters
should be inserted immediately after the event of interest has occured.

```python
emit_trial_start(...)
emit_response(...)
emit_trial_end(...)
```

If it was not emitted, for all intents and purposes, it did not happen!

---

## Step 8. Event record and logging

Emitters emit events to the event stream held by the `EventRecorder`. Loggers
read the event stream and log to file what ever is new since the last time.

You want to emit events immediately when they happen, but logging can happen
later, in batches, when you can afford the time-cost of writing to disk.

---

## Step 9. Trial loop behavior

Cannonical structure:

```
while state not done:
    events → actions
    actions → decisions
    decisions → state transitions
```

Trials are state machines, not sequences of instructions.

---

## Step 10. Development workdlow


This design *replaces* the "watch what happens" workflow. By the "watch what
happens" workflow, I mean you do a little experiment building, then you run the
experiment as if you were a particpant, seeing everything displayed on the
screen and physically making actions to progress the experiment. Instead,
everything you care about the experiment should be logged. Critically, logging
is completely orthogonal to rendering visuals, and does not care if it is a
person or a computer who is generating the events that get translated into
actions and behaviors. This means that, when you are developing, you should
postpone using the PsychoPy rendering backend until you are satisfied with the
behavior of the experiment: everything that you want to be emitted is emitted
when it should be emitted (and being logged). Once the structure of your
experiment is correct, only then should you enage the PsychoPy backend. At that
point, all that will be left to is fine tune your display layouts and visual
asthetics.

You debug behavior through *logs*, not visuals.

Recommended workflow:

1. Define actions + config
2. Use scripted input to verify logic
3. Check event logs to verify correctness.
4. Add visualization (i.e., rendering) once the logic is correct.

### Define a DEV role

Roles let you test quickly without rewriting your task.

### What is a role, anyway?

✅ What roles are

💥 Different configurations of the SAME task

| Role     | Purpose         |
|----------|-----------------|
| DEV      | fast testing    |
| PRACTICE | learning        |
| MAIN     | real experiment |


✅ What roles are NOT

❌ Different tasks
❌ Different code


👉 Only configuration changes

---

# Things missing in v2

* We do not introduce `displays`.

* We do not introduce `plans` or how session plans are specified as YAML assets.

* We do not introduce how YAML is used for writing instructions, and where
  these files should be placed within the project directory.

