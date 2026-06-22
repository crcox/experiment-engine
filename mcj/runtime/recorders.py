from typing import Protocol

class RecorderAdapter(Protocol):
    def handle_event(self, event: dict) -> None:
        """Receive a semantic event emitted by the experiment"""
        ...


class DebugRecorderAdapter(RecorderAdapter):
    def handle_event(self, event: dict) -> None:
        print("[RecorderAdapter]", event)
