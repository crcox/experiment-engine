import time

from mcj.runtime.session import SessionRuntime
from mcj.runtime.emitters import (
        emit_alignment,
        emit_wait_for_trigger_start, emit_wait_for_trigger_end,
        emit_wait_for_command_start, emit_wait_for_command_end,
    )
from mcj.runtime.end_reasons import EndReason
from mcj.runtime.exceptions import ExperimentAbort, EscapePressed, CedrusAlignmentTimout, WaitForTriggerTimout
from mcj.runtime.input_events import ButtonEvent, TriggerEvent
from mcj.runtime.input import InputMode
from mcj.runtime.cedrus import CedrusAdapter, Alignment

WAIT_FOR_TRIGGER_TIMEOUT_SECONDS = None

def wait_for_block_start(session: SessionRuntime) -> float:
    ctx = session.ctx

    cedrus_adapter = ctx.input.require_adapter(CedrusAdapter)

    emit_wait_for_trigger_start(ctx)
    end_reason = EndReason.COMPLETE
    end_cause = None

    trigger_received = False
    alignment_emitted = False
    t0_system_seconds = None

    try:
        if ctx.input_mode == InputMode.SIMULATED_DIRECT:
            t0_system_seconds = ctx.now()
            return t0_system_seconds

        # --- Ensure the adapter and device hold no stale trigger events ---
        cedrus_adapter.clear()

        start = ctx.now()
        while not trigger_received:
            if (
                    WAIT_FOR_TRIGGER_TIMEOUT_SECONDS is not None
                    and ctx.now() - start > WAIT_FOR_TRIGGER_TIMEOUT_SECONDS
                ):
                raise WaitForTriggerTimout

            if not cedrus_adapter.is_aligned:
                t_before = ctx.now()
                cedrus_adapter.set_last_t_before(t_before)

            session.maybe_step_simulation()
            ctx.input.update()

            for event in ctx.input.peek_events():
                if isinstance(event, ButtonEvent) and event.is_press:
                    if event.code == "escape":
                        raise EscapePressed

                if isinstance(event, TriggerEvent) and event.is_press:
                    t0_system_seconds = event.time
                    trigger_received = True

            time.sleep(0.0005)

            if cedrus_adapter.is_aligned and not alignment_emitted:
                alignment = cedrus_adapter.require_alignment()
                emit_alignment(
                    ctx,
                    t0_device=float(alignment.t0_device_ms / 1000),
                    t0_system=alignment.t0_system_s,
                )
                alignment_emitted = True

        if t0_system_seconds is None:
            # I don't think it should be possible to end up here...
            raise RuntimeWarning("A trigger never occured")

        return t0_system_seconds

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_wait_for_trigger_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )


def wait_for_command(session: SessionRuntime) -> ButtonEvent:
    ctx = session.ctx

    emit_wait_for_command_start(ctx)
    end_reason = EndReason.COMPLETE
    end_cause = None

    try:
        print(
            "[DEBUG] wait_for_command clear:",
            len(ctx.input.peek_events())
        )
        ctx.input.clear()
        while True:

            session.maybe_step_simulation()
            ctx.input.update()

            for event in ctx.input.pop_events():
                print(
                    "[DEBUG POP]",
                    type(event).__name__,
                    getattr(event, "code", None),
                    event.time,
                )
                if isinstance(event, ButtonEvent) and event.is_press:
                    if event.code == "escape":
                        raise EscapePressed

                    if event.code == "space":
                        return event

            time.sleep(0.0005)

    except ExperimentAbort as e:
        end_reason = e.reason
        end_cause = e.cause
        raise

    except Exception as e:
        end_reason = EndReason.ERROR
        end_cause = type(e).__name__
        raise

    finally:
        emit_wait_for_command_end(
            ctx,
            reason=end_reason,
            cause=end_cause
        )

def sync_cedrus_and_experiment_clocks(session: SessionRuntime) -> Alignment:
    ctx = session.ctx

    if ctx.input_mode == InputMode.SIMULATED_DIRECT:
        t = ctx.now()
        return Alignment(
            t0_system_s=t,
            t0_device_ms=round(t*1000)
        )

    cedrus_adapter = ctx.input.require_adapter(CedrusAdapter)

    if cedrus_adapter.is_aligned:
        alignment = cedrus_adapter.require_alignment()
        return alignment

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

