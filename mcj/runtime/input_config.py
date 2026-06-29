from typing import Sequence

from mcj.runtime.input import InputManager, InputMode, InputChannel, InputAdapter
from mcj.runtime.input_types import AdapterFactory
from mcj.runtime.keyboard import KeyboardAdapter
from mcj.runtime.cedrus import CedrusAdapter
from mcj.runtime.scripting.direct_driver import DirectScriptDriver
from mcj.runtime.session_info import SessionInfo
from mcj.runtime.time import Clock

from mcj.runtime.scripting.cedrus_driver import CedrusScriptDriver
from mcj.runtime.scripting.keyboard_driver import KeyboardScriptDriver

from mcj.config.experiment import ENVIRONMENT_CHANNELS

from mcj.adapters.pyxid2.mock import MockXidDevice

def resolve_input_adapters(session_info: SessionInfo, clock: Clock) -> list[InputAdapter]:
    input_mode = session_info.input_mode
    adapters: list[InputAdapter] = []

    # --- global override (event-level simulation)
    if input_mode == InputMode.SIMULATED_DIRECT:
        # None channel = channel-less (direct scripted input, no devices)
        return adapters

    # --- otherwise: compose channels
    channels = ENVIRONMENT_CHANNELS[session_info.environment]

    for channel in channels:
        key = (input_mode, channel)
        if key not in ADAPTER_FACTORIES:
            raise RuntimeError(
                f"No implementation defined for channel={channel} with input_mode={input_mode}"
            )
        factory = ADAPTER_FACTORIES[key]
        adapters.append(factory(clock, session_info))

    return adapters



def resolve_script_drivers(
    session_info: SessionInfo,
    clock: Clock,
    input_manager: InputManager
):
    if session_info.script is None:
        return []

    adapters = input_manager.get_adapters()

    drivers = []

    if session_info.input_mode == InputMode.SIMULATED_DIRECT:
        drivers.append(DirectScriptDriver(clock, input_manager))

    # --- Cedrus scripting via mock device ---
    cedrus_device = get_mock_cedrus_device(adapters)

    if cedrus_device is not None:
        drivers.append(
            CedrusScriptDriver(
                device=cedrus_device
            )
        )

    # --- Keyboard scripting via KeyboardAdapter ---
    for a in adapters:
        if isinstance(a, KeyboardAdapter):
            drivers.append(
                KeyboardScriptDriver(clock, adapter=a)
            )

    return drivers

def build_keyboard(clock: Clock, _: SessionInfo):
    return KeyboardAdapter(
        clock=clock
    )

def build_cedrus(clock: Clock, _: SessionInfo):
    return CedrusAdapter(clock=clock, device=None)

def build_cedrus_mock(clock: Clock, _: SessionInfo):
    device = MockXidDevice()
    return CedrusAdapter(
        clock=clock,
        device=device
    )

def get_mock_cedrus_device(adapters: Sequence[InputAdapter]) -> MockXidDevice | None:
    for a in adapters:
        if isinstance(a, CedrusAdapter):
            device = a.device
            if isinstance(device, MockXidDevice):
                return device

    return None


ADAPTER_FACTORIES: dict[tuple[InputMode, InputChannel | None], AdapterFactory] = {
    (InputMode.REAL            , InputChannel.KEYBOARD): build_keyboard,
    (InputMode.SIMULATED_DEVICE, InputChannel.KEYBOARD): build_keyboard,
    (InputMode.REAL            , InputChannel.CEDRUS  ): build_cedrus,
    (InputMode.SIMULATED_DEVICE, InputChannel.CEDRUS  ): build_cedrus_mock,
}

