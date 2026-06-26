import time
from pathlib import Path

from mcj.config.paths import paths
from mcj.runtime.backend import RenderBackend
from mcj.runtime.setup import build_session
from mcj.runtime.scripting.events import ScriptEvent
from mcj.dev.session_info import StaticSessionInfoProvider
from mcj.runtime.synchronization import sync_cedrus_and_experiment_clocks

script = {
    "without_time": [
        ScriptEvent(time=None, type="button", code="1", target="cedrus"),
        ScriptEvent(time=None, type="button", code="2", target="cedrus"),
        ScriptEvent(time=None, type="button", code="3", target="cedrus"),
    ],
    "with_time": [
        ScriptEvent(time=0.0, type="button", code="1", target="cedrus"),
        ScriptEvent(time=0.5, type="button", code="2", target="cedrus"),
        ScriptEvent(time=1.0, type="button", code="3", target="cedrus"),
    ],
    "trigger_alignment": [
        ScriptEvent(time=0.5, type="button", code=0, target="cedrus"),
        ScriptEvent(time=1.0, type="trigger", code=4, target="cedrus"),
    ],
    "abort_alignment": [
        ScriptEvent(time=0.4, type="button", code="escape", target="keyboard"),
        ScriptEvent(time=0.5, type="trigger", code=4, target="cedrus"),
    ],
}

DEV_ENVIRONMENT = True
RENDER_BACKEND = RenderBackend.FAKE

def test_simulation_backend(with_time: bool=False):
    provider = StaticSessionInfoProvider({
        "subject_id": 999,
        "environment": "local",
        "profile": "dev",
        "input_mode": "simulated",
        "script": script["with_time"] if with_time else script["without_time"],
    })

    session_info = provider.get_session_info("simulation test")

    paths.initialize(
        root=Path.cwd(),
    )

    session, _, _ = build_session(session_info, backend=RENDER_BACKEND)

    print("=== START SIMULATION ===")

    while True:

        # --- 1. Step simulation ---
        session.maybe_step_simulation()

        # --- 2. Update input system ---
        session.ctx.input.update()

        # --- 3. Pull events ---
        events = session.ctx.input.pop_events()

        for ev in events:
            print(f"[INPUT EVENT] {ev}")

        # --- 4. Exit condition ---
        if session.scheduler and session.scheduler.is_finished:
            print("=== SCRIPT FINISHED ===")
            break

        time.sleep(0.016)  # ~60 Hz loop


def test_alignment():
    provider = StaticSessionInfoProvider({
        "subject_id": 999,
        "environment": "scanner",
        "profile": "dev",
        "input_mode": "simulated",
        "script": script["trigger_alignment"],
    })

    session_info = provider.get_session_info("alignment test")

    paths.initialize(
        root=Path.cwd(),
    )

    session, _, _ = build_session(session_info, backend=RENDER_BACKEND)

    print("=== START ALIGNMENT TEST ===")

    alignment = sync_cedrus_and_experiment_clocks(session)

    print("=== ALIGNMENT RESULT ===")
    print(alignment)


if __name__ == "__main__":
    test_alignment()
