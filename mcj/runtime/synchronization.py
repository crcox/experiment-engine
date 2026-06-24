import time

from dataclasses import dataclass

from mcj.runtime.time import Clock
from mcj.runtime.session import SessionRuntime
from mcj.runtime.emitters import emit_alignment_start, emit_alignment_end
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import ExperimentAbort, EscapePressed, CedrusAlignmentTimout
from mcj.runtime.input_events import ButtonEvent
from mcj.runtime.input import InputMode
from mcj.runtime.cedrus import CedrusAdapter, Alignment

@dataclass(frozen=True)
class SimpleAlignment:
    t0_system: float

def sync_cedrus_and_experiment_clocks(session: SessionRuntime) -> Alignment:
    ctx = session.ctx

    if ctx.input_mode == InputMode.SCRIPTED:
        t = ctx.now()
        return Alignment(
            t0_system_s=t,
            t0_device_ms=round(t*1000)
        )

    cedrus_adapter = ctx.input.require_adapter(CedrusAdapter)

    emit_alignment_start(ctx)
    t0_device = None
    t0_system = None
    end_reason = EndReason.COMPLETE
    end_cause = None
    try:
        # --- Ensure the adapter and device hold no stale trigger events ---
        cedrus_adapter.clear()

        # --- Clear alignment data from the adapter ---
        cedrus_adapter.reset_alignment()

        start = ctx.now()
        while not cedrus_adapter.is_aligned:
            if ctx.now() - start > 5.0:
                raise CedrusAlignmentTimout

            t_before = ctx.now()
            cedrus_adapter.set_last_t_before(t_before)

            session.maybe_step_simulation()
            ctx.input.update()

            for event in ctx.input.peek_events():
                if isinstance(event, ButtonEvent) and event.is_press:
                    if event.code == "escape":
                        raise EscapePressed

            time.sleep(0.0005)

        alignment = cedrus_adapter.require_alignment()

        t0_device = float(alignment.t0_device_ms / 1000)
        t0_system = alignment.t0_system_s
        end_reason = EndReason.COMPLETE
        end_cause = None

        return alignment

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_alignment_end(
            ctx,
            t0_device=t0_device,
            t0_system=t0_system,
            reason=end_reason,
            cause=end_cause
        )


def sync_cedrus_and_experiment_clocks_testing(cedrus_adapter: CedrusAdapter, now: Clock) -> Alignment:

    t0_device = None
    t0_system = None
    end_reason = EndReason.COMPLETE
    end_cause = None
    try:
        # --- Ensure the adapter and device hold no stale trigger events ---
        cedrus_adapter.clear()

        # --- Clear alignment data from the adapter ---
        cedrus_adapter.reset_alignment()

        while not cedrus_adapter.is_aligned:
            t_before = now()
            cedrus_adapter.set_last_t_before(t_before)

            cedrus_adapter.update()

            for event in cedrus_adapter.peek_events():
                if isinstance(event, ButtonEvent) and event.is_press:
                    if event.code == "escape":
                        raise EscapePressed

            time.sleep(0.0005)

        alignment = cedrus_adapter.require_alignment()

        t0_device = float(alignment.t0_device_ms / 1000)
        t0_system = alignment.t0_system_s
        end_reason = EndReason.COMPLETE
        end_cause = None

        return alignment

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        print(
            f"t0_device={t0_device}",
            f"t0_system={t0_system}",
            f"reason={end_reason}",
            f"cause={end_cause}"
        )

