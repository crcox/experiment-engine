from mcj.runtime.input import InputBackend, AdapterType, InputAdapter
from mcj.runtime.input_types import AdapterFactory
from mcj.runtime.keyboard import KeyboardAdapter
from mcj.runtime.cedrus import CedrusAdapter
from mcj.runtime.scripted import ScriptedInputAdapter
from mcj.runtime.session_info import SessionInfo
from mcj.runtime.time import Clock

from mcj.config.experiment import ENVIRONMENT_CHANNELS, CHANNEL_IMPLEMENTATIONS

from mcj.xid.mock import MockXidDevice

def resolve_input_adapters(session_info: SessionInfo, clock: Clock) -> list[InputAdapter]:
    input_backend = session_info.input_backend


    # --- global override (event-level simulation)
    if input_backend == InputBackend.SCRIPTED:
        return [
            ADAPTER_FACTORIES[AdapterType.SCRIPTED](clock, session_info)
        ]

    # --- otherwise: compose channels
    channels = ENVIRONMENT_CHANNELS[session_info.environment]

    adapters = []
    for channel in channels:
        if input_backend not in CHANNEL_IMPLEMENTATIONS[channel]:
            raise RuntimeError(
                f"No implementation defined for channel={channel} with backend={input_backend}"
            )
        impl_key = CHANNEL_IMPLEMENTATIONS[channel][input_backend]
        factory = ADAPTER_FACTORIES[impl_key]
        adapters.append(factory(clock, session_info))

    return adapters


def build_keyboard(clock: Clock, _: SessionInfo):
    return KeyboardAdapter(
        clock=clock,
        allowed_keys={"f", "j", "space", "escape"}
    )

def build_cedrus(clock: Clock, _: SessionInfo):
    return CedrusAdapter(clock=clock, device=None)

def build_cedrus_mock(clock: Clock, _: SessionInfo):
    return CedrusAdapter(
        clock=clock,
        device=MockXidDevice()
    )

def build_scripted(clock: Clock, ctx: SessionInfo):
    if ctx.script is None:
        raise RuntimeError("Attempting to build a ScriptedInputAdapted, but no script was provided")

    return ScriptedInputAdapter(
        clock=clock,
        script=ctx.script
    )

ADAPTER_FACTORIES: dict[AdapterType, AdapterFactory] = {
    AdapterType.KEYBOARD: build_keyboard,
    AdapterType.CEDRUS: build_cedrus,
    AdapterType.CEDRUS_MOCK: build_cedrus_mock,
    AdapterType.SCRIPTED: build_scripted,
}

