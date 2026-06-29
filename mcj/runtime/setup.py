from typing import Callable
from pathlib import Path

from mcj.config.experiment import CONFIG_BY_PROFILE
from mcj.config.paths import paths

from mcj.plans.criterion_judgment.loader import load_criterion_judgment_plan

from mcj.runtime.config_types import TaskConfigBundle
from mcj.runtime.recorders import DebugRecorderAdapter
from mcj.runtime.session import SessionRuntime
from mcj.runtime.session_context import SessionContext
from mcj.runtime.events import SESSION_EVENTS, EventRecorder
from mcj.runtime.environments import Environment
from mcj.runtime.backend import RenderBackend
from mcj.runtime.display_profile import (
    LAPTOP_DISPLAY,
    SCANNER_DISPLAY,
    SCANNER_DEBUG,
    NULL_DISPLAY,
)

from mcj.runtime.input import InputManager
from mcj.runtime.input_config import resolve_input_adapters, resolve_script_drivers, get_mock_cedrus_device
from mcj.runtime.session_info import SessionInfo

from mcj.runtime.scripting.scheduler import ScriptScheduler

from mcj.io.loggers import EventTypeLogger

from mcj.runtime.setup_types import TaskAssetPaths
from mcj.stimuli.loader import load_word_metadata_csv

from mcj.adapters.psychopy.display import PsychoPyStimFactory
from mcj.adapters.fake.display import FakeFactory


def build_session(
    session_info: SessionInfo,
    backend: RenderBackend
) -> tuple[SessionRuntime, TaskConfigBundle, EventTypeLogger]:

    data_dir = resolve_data_dir(session_info)
    assets = resolve_assets(session_info)

    profile = session_info.profile
    word_table = load_word_metadata_csv(
        base_assets_dir=assets.base
    )
    clock = resolve_clock(backend)

    input_adapters = resolve_input_adapters(
        session_info,
        clock
    )

    input_manager = InputManager(input_adapters)
    script_drivers = resolve_script_drivers(session_info, clock, input_manager)

    block_start_hooks: list[Callable] = []
    block_end_hooks: list[Callable] = []

    cedrus_device = get_mock_cedrus_device(input_adapters)

    if cedrus_device and session_info.enable_triggers:
        block_start_hooks.append(cedrus_device.start_auto_trigger)
        block_end_hooks.append(cedrus_device.stop_auto_trigger)

    # --- Define Scheduler (for SCRIPTED and SIMULATED environments/backends) ---
    scheduler = None
    if session_info.script is not None:
        scheduler = ScriptScheduler(clock=clock, script=session_info.script)
 
    # --- Define Session Context ---
    ctx = SessionContext(
        _plans={
            'criterion_judgment': load_criterion_judgment_plan(
                profile_assets_dir=assets.profile,
                profile=profile,
                subject_id=session_info.subject_id,
                word_table=word_table
            )
        },
        assets=assets,
        data_dir=data_dir,
        clock=clock,
        input=input_manager,
        input_mode=session_info.input_mode,
        recorder=EventRecorder(adapters=(DebugRecorderAdapter(),)),
    )

    # --- Define Session Runtime ---
    session = SessionRuntime(
        ctx=ctx,
        environment=session_info.environment,
        scheduler=scheduler,
        drivers=tuple(script_drivers),
        on_block_start=tuple(block_start_hooks),
        on_block_end=tuple(block_end_hooks),
    )

    # --- Configure trial environments ---
    cfg = CONFIG_BY_PROFILE[profile]

    # --- Instantiate loggers ---
    session_logger = EventTypeLogger(
        data_dir / "session.events.jsonl",
        SESSION_EVENTS
    )

    return session, cfg, session_logger


def resolve_display(session_info: SessionInfo, backend: RenderBackend, dev_environment: bool=False):
    if backend == RenderBackend.PSYCHOPY:
        if session_info.environment == Environment.LOCAL:
            display = LAPTOP_DISPLAY
        elif session_info.environment == Environment.SCANNER:
            if dev_environment:
                display = SCANNER_DEBUG
            else:
                display = SCANNER_DISPLAY

        else:
            raise RuntimeError(f"Unhandled environment={session_info.environment}")

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
        factory = FakeFactory(verbose=True)
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


def resolve_data_dir(session_info: SessionInfo) -> Path:
    task = session_info.task
    profile = session_info.profile
    subject_id = session_info.subject_id
    return paths.data_dir_for_profile(task, profile, subject_id)

def resolve_assets(session_info: SessionInfo) -> TaskAssetPaths:
    task = session_info.task
    profile = session_info.profile
    return paths.asset_paths_for_profile(task, profile)

