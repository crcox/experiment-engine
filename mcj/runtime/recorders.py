from typing import Protocol, Mapping

class RecorderAdapter(Protocol):
    def handle_event(self, event: Mapping) -> None:
        """Receive a semantic event emitted by the experiment"""
        ...


class DebugRecorderAdapter(RecorderAdapter):
    def handle_event(self, event: Mapping) -> None:
        print("[RecorderAdapter]", event)
