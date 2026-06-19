from typing import Protocol, Literal, overload

from mcj.runtime.session_context import SessionContext
from mcj.runtime.end_reasons import EndReason

class EmitterWithoutReason(Protocol):
    def __call__(self, ctx: SessionContext) -> None: ...


class EmitterWithReason(Protocol):
    def __call__(
            self,
            ctx: SessionContext, *,
            reason: EndReason,
            cause: str | None,
        ) -> None: ...

Emitter = EmitterWithReason | EmitterWithoutReason

class IndexedEmitterWithoutReason(Protocol):
    def __call__(self, ctx: SessionContext, index: int) -> None: ...


class IndexedEmitterWithReason(Protocol):
    def __call__(
            self,
            ctx: SessionContext, *,
            index: int,
            reason: EndReason,
            cause: str | None,
        ) -> None: ...

IndexedEmitter = IndexedEmitterWithReason | IndexedEmitterWithoutReason

@overload
def make_emitter(event_type: str, *, has_reason: Literal[False] = False) -> EmitterWithoutReason: ...

@overload
def make_emitter(event_type: str, *, has_reason: Literal[True]) -> EmitterWithReason: ...

def make_emitter(event_type: str, *, has_reason: bool=False) -> Emitter:
    if has_reason:
        def emit_with_reason(ctx: SessionContext, *, reason: EndReason, cause: str | None):
            ctx.recorder.emit({
                "type": event_type,
                "time": ctx.now(),
                "reason": reason.value,
                "cause": cause,
            })

        return emit_with_reason

    else:
        def emit_simple(ctx: SessionContext):
            ctx.recorder.emit({
                "type": event_type,
                "time": ctx.now(),
            })

        return emit_simple

@overload
def make_indexed_emitter(event_type: str, *, has_reason: Literal[False] = False) -> IndexedEmitterWithoutReason: ...

@overload
def make_indexed_emitter(event_type: str, *, has_reason: Literal[True]) -> IndexedEmitterWithReason: ...

def make_indexed_emitter(event_type: str, *, has_reason: bool=False) -> IndexedEmitter:
    if has_reason:
        def emit_with_reason(ctx: SessionContext, index: int, reason: EndReason, cause: str | None):
            ctx.recorder.emit({
                "type": event_type,
                "time": ctx.now(),
                "index": index,
                "reason": reason.value,
                "cause": cause,
            })

        return emit_with_reason

    else:
        def emit_simple(ctx: SessionContext, index: int):
            ctx.recorder.emit({
                "type": event_type,
                "time": ctx.now(),
                "index": index,
            })

        return emit_simple
