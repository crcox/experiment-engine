# 🔌 Adapters (External Integrations)

Adapters connect the runtime system to external tools and hardware.

Examples:
- PsychoPy (visual display)
- Cedrus (response boxes)
- Keyboard input
- Fake/mock adapters for development

Adapters implement runtime-facing interfaces, such as:
- `StimFactory`
- `InputAdapter`

## Key Principle

The runtime depends on adapter *interfaces*, not concrete implementations.

This allows:
- swapping hardware without changing task code
- testing with mock adapters
- clean separation of concerns

Adapters sit outside the main execution pipeline and are injected during setup.

           ┌──────────────────────┐
           │       ADAPTERS       │
           │ psychopy, cedrus,    │
           │ fake, keyboard, etc. │
           └──────────┬───────────┘
                      ↓
        ┌────────────────────────────┐
        │   runtime (input/display)  │
        └──────────┬─────────────────┘
                   ↓
        ┌────────────────────────────┐
        │   execution + domain       │
        └────────────────────────────┘

---

## Full Architecture with Adapters

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
                └──────────┬─────────────────┘
                           ↓
                ┌────────────────────────────┐
                │   ExecutionContext         │
                └──────────┬─────────────────┘
                           ↓
                ┌────────────────────────────┐
                │ runtime core               │
                │ (mapping, profiles, term)     │
                └──────────┬─────────────────┘
                           ↓
                ┌────────────────────────────┐
                │ session / base types       │
                └──────────┬─────────────────┘
                           ↓
                ┌────────────────────────────┐
                │ input / time / events      │
                └──────────┬─────────────────┘

        ───────────────────────────────────────────
             EXTERNAL INTEGRATION (ADAPTERS)
        ───────────────────────────────────────────

            ┌───────────────┐   ┌───────────────┐
            │ psychopy      │   │  cedrus       │
            ├───────────────┤   ├───────────────┤
            │ fake display  │   │ keyboard      │
            └──────┬────────┘   └──────┬────────┘
                   ↓                   ↓
            ┌──────────────────────────────────┐
            │ runtime.input / display APIs     │
            └──────────────────────────────────┘



