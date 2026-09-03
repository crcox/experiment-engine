
The construction of the KeyboardAdapter is triggered and parameterized by `build_keyboard()`, which is defined in `runtime/input_config.py` and is stored in a dictionary as a factory:

```python

ADAPTER_FACTORIES: dict[tuple[InputMode, InputChannel | None], AdapterFactory] = {
    (InputMode.REAL            , InputChannel.KEYBOARD): build_keyboard,
    (InputMode.SIMULATED_DEVICE, InputChannel.KEYBOARD): build_keyboard,
    (InputMode.REAL            , InputChannel.CEDRUS  ): build_cedrus,
    (InputMode.SIMULATED_DEVICE, InputChannel.CEDRUS  ): build_cedrus_mock,
}

```

Which adapter the session will use is resolved in `resolve_input_adapters()`, which is called by `build_session()` which is defined in `runtime/setup.py`.

The `kb=` argument is never used.

PsychopyClockAdapter is only used when initializing a keyboard device to be held by the KeyboardAdapter.

The clock is resolved as a Callable[[], float] that just returns the current time on that clock. This is defined and handled in `runtime/setup.py`.

```python
def resolve_clock(backend: RenderBackend) -> Callable[[], float]:
    if backend == RenderBackend.PSYCHOPY:
        from psychopy.clock import monotonicClock
        return monotonicClock.getTime

    elif backend == RenderBackend.FAKE:
        from time import perf_counter 
        return perf_counter

    else:
        raise RuntimeError("Unknown render backend")

```



project_context.md|5 col 24| - There is currently a KeyboardAdapter and a CedrusAdapter (Cedrus uses device clock in ms)
mcj\runtime\keyboard.py|27 col 7| class KeyboardAdapter(InputAdapter):
mcj\runtime\input_config.py|5 col 34| from mcj.runtime.keyboard import KeyboardAdapter
mcj\runtime\input_config.py|68 col 34| # --- Keyboard scripting via KeyboardAdapter ---
mcj\runtime\input_config.py|70 col 26| if isinstance(a, KeyboardAdapter):
mcj\runtime\input_config.py|78 col 12| return KeyboardAdapter(
mcj\runtime\scripting\keyboard_driver.py|2 col 34| from mcj.runtime.keyboard import KeyboardAdapter
mcj\runtime\scripting\keyboard_driver.py|10 col 14| Drives a KeyboardAdapter using scripted events.
mcj\runtime\scripting\keyboard_driver.py|17 col 15| _adapter: KeyboardAdapter
mcj\runtime\scripting\keyboard_driver.py|22 col 18| adapter: KeyboardAdapter,
