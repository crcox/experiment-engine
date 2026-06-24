
# MCJ Architecture

This document describes the high-level architecture of the MCJ experiment framework.

The system is organized into **strict layers**, with **one-directional dependencies**. This ensures:

- No circular imports
- Clear separation of concerns
- Strong type safety with generics
- Ease of extension and teaching

---

# 🧭 Overview

The architecture follows this layered structure:

> BASE → CORE → EXECUTION → DOMAIN → CONFIG → ENTRYPOINT

Each layer may depend on layers below it, but never above.

            ┌──────────────┐
            │   main.py    │
            └──────┬───────┘
                   ↓
            ┌─────────────────────┐
            │ config/experiment   │
            └──────┬──────────────┘
                   ↓
        ┌────────────────────────────┐
        │     tasks / routines       │
        │     (domain logic)         │
        └──────────┬─────────────────┘
                   ↓
        ┌────────────────────────────┐
        │   execution.py             │
        │ ExecutionContext[ActionT]  │
        └──────────┬─────────────────┘
                   ↓
        ┌─────────────────────────────┐
        │ runtime core                │
        │ roles, mapping, termination │
        └──────────┬──────────────────┘
                   ↓
        ┌────────────────────────────┐
        │ base layer                 │
        │ SessionRuntime             │
        │ SessionContext             │
        │ TaskProfileConfigs                 │
        └──────────┬─────────────────┘
                   ↓
        ┌────────────────────────────┐
        │ input, time, events, io    │
        └────────────────────────────┘

---

# 🧱 Layers

## 1. Base Layer (Foundations)

**Modules:**
- `runtime/session_context.py`
- `runtime/session.py`
- `runtime/config_types.py`

**Responsibilities:**
- Define shared, non-generic data structures
- Represent the environment of a running experiment

**Key Types:**
- `SessionContext` — raw runtime environment (clock, input, events, etc.)
- `SessionRuntime` — wrapper containing session-level properties (e.g., mode)
- `TaskProfileConfigs` — typed grouping of role configs

✅ Must not depend on:
- mapping
- roles
- tasks
- config

---

## 2. Runtime Core (Generic Mechanics)

**Modules:**
- `runtime/mapping.py`
- `runtime/termination.py`
- `runtime/roles.py`

**Responsibilities:**
- Define fully generic runtime behavior
- Provide reusable primitives for tasks and routines

**Key Concepts:**
- `EventMapping[ActionT]` — event → action
- `TerminationCondition[ActionT]` — when a state ends
- `TaskProfileConfig[ActionT]` — per-state behavior definitions

✅ Depends on:
- Base layer

❌ Must not depend on:
- ExecutionContext
- Tasks or routines
- Config

---

## 3. Execution Layer (Binding Generics)

**Modules:**
- `runtime/execution.py`

**Responsibilities:**
- Bind session-level data to role-level behavior

**Key Types:**
- `ExecutionContext[ActionT]`

> ExecutionContext = SessionRuntime + TaskProfileConfig[ActionT]

This is the only place where:
- session data and
- action-specific behavior

are combined.

✅ Depends on:
- Base layer
- Runtime core

---

## 4. Domain Layer (Tasks and Routines)

**Modules:**
- `tasks/*`
- `routines/*`
- `plans/*`

**Responsibilities:**
- Define experiment behavior
- Implement task logic and flow
- Use runtime primitives to execute behavior

**Examples:**
- `run_trial()`
- `present_instructions()`
- task-specific mappings and displays

✅ Depends on:
- ExecutionContext
- Runtime core
- Base layer

❌ Must not depend on:
- config

---

## 5. Config Layer (Composition)

**Modules:**
- `config/experiment.py`
- task-specific config modules

**Responsibilities:**
- Assemble TaskProfileConfigs
- Define experiment structure
- Connect tasks and routines

✅ Depends on:
- tasks
- routines
- runtime

❌ Nothing depends on config

---

## 6. Entrypoint

**Modules:**
- `main.py`

**Responsibilities:**
- Wire everything together
- Build session
- Select role
- Run the experiment

---

# 🔁 Data Flow

At runtime, data flows as follows:

```
SessionContext
↓
SessionRuntime
↓
ExecutionContext[ActionT]
↓
TaskProfileConfig[ActionT]
↓
Mapping / Termination
↓
Routine / Task logic
```

---

# 🧠 Action Domains

Each routine defines its own **Action type**.

| Routine          | Action Type            |
| ---------------- | ---------------------- |
| Instructions     | `InstructionAction`    |
| Criterion Task   | `CJAction`             |

Each Action type corresponds to its own:

- `TaskProfileConfig[ActionT]`
- `ExecutionContext[ActionT]`
- mapping + termination behavior

---

# ⚖️ Design Principles

## 1. One-directional dependencies

> Lower layers never import higher layers

---

## 2. Separate shared vs typed data

- Shared data → Base layer
- Action-specific data → Generic types

---

## 3. Config is composition only

- Config assembles components
- It is never imported by runtime or tasks

---

## 4. One Action type per execution context

> ExecutionContext[CJAction] ≠ ExecutionContext[InstructionAction]

---

## 5. Mapping uses Session-level data

Mappings depend on:

> SessionRuntime

not on `ExecutionContext`.

---

# 🚫 Anti-patterns to avoid

❌ Importing config from tasks  
❌ Putting shared types in high-level modules  
❌ Mixing Action types in one TaskProfileConfig  
❌ Using `Any` to bypass generics  
❌ Creating bidirectional module dependencies  

---

# 📌 Summary

The system is built around:

- Generic runtime mechanics
- Task-specific semantics
- Clean layering with no cycles

This allows:

✅ reuse  
✅ extensibility  
✅ strong static typing  
✅ teachability  

---
