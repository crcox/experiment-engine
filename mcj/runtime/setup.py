from typing import Callable

from mcj.config.experiment import CONFIG_BY_ROLE
from mcj.config.paths import paths

from mcj.plans.criterion_judgment.loader import load_criterion_judgment_plan

from mcj.runtime.session_context import SessionContext
from mcj.runtime.events import SESSION_EVENTS, EventRecorder
from mcj.runtime.modes import Mode
from mcj.runtime.backend import RenderBackend
from mcj.runtime.display_profile import (
    LAPTOP_DISPLAY,
    SCANNER_DISPLAY,
    SCANNER_DEBUG,
    NULL_DISPLAY,
)

from mcj.runtime.input import InputManager, InputBackend
from mcj.runtime.input_config import resolve_input_adapters
from mcj.runtime.session_info import SessionInfo

from mcj.io.loggers import EventTypeLogger

from mcj.stimuli.loader import load_word_metadata_csv

from mcj.adapters.psychopy.display import PsychoPyStimFactory
from mcj.adapters.fake.display import FakeFactory


def build_session(session_info: SessionInfo, backend: RenderBackend):

    role = session_info.role

    word_table = load_word_metadata_csv()

    clock = resolve_clock(backend)


    input_adapters = resolve_input_adapters(
        session_info,
        clock
    )

    # --- Define Session Context ---
    ctx = SessionContext(
        _plans={
            'criterion_judgment': load_criterion_judgment_plan(
                role=role,
                subject_id=session_info.subject_id,
                word_table=word_table
            )
        },
        clock=clock,
        input=InputManager(input_adapters),
        input_backend=InputBackend(session_info.input_backend),
        recorder=EventRecorder(),
    )

    # --- Configure trial modes ---
    cfg = CONFIG_BY_ROLE[role]

    # --- Instantiate loggers ---
    session_logger = EventTypeLogger(
        paths.DATA / "session.events.jsonl",
        SESSION_EVENTS
    )

    return ctx, cfg, session_logger


def resolve_display(session_info: SessionInfo, backend: RenderBackend, dev_mode: bool=False):
    if backend == RenderBackend.PSYCHOPY:
        if session_info.mode == Mode.PRACTICE:
            display = LAPTOP_DISPLAY
        elif session_info.mode == Mode.SCANNER:
            if dev_mode:
                display = SCANNER_DEBUG
            else:
                display = SCANNER_DISPLAY

        else:
            raise RuntimeError(f"Unhandled mode={session_info.mode}")

        from psychopy.visual.window import Window

        win = Window(
            size=display.size,
            color=display.color,
            colorSpace=display.colorSpace,
            units=display.units,
            fullscr=display.fullscr
        )
        factory = PsychoPyStimFactory(win)

    elif backend == RenderBackend.FAKE:
        factory = FakeFactory()
        display = NULL_DISPLAY
    else:
        raise RuntimeError("Unknown render backend")

    return factory, display


def resolve_clock(backend: RenderBackend) -> Callable[[], float]:
    if backend == RenderBackend.PSYCHOPY:
        from psychopy.clock import monotonicClock
        return monotonicClock.getTime

    elif backend == RenderBackend.FAKE:
        from time import perf_counter 
        return perf_counter

    else:
        raise RuntimeError("Unknown render backend")
