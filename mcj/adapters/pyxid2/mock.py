import time
import threading
from collections import deque

from mcj.adapters.pyxid2.types import XidEvent, XidDeviceLike

class MockXidDevice(XidDeviceLike):
    response_queue: deque[XidEvent]
    _device_queue: deque[XidEvent]
    _start_time: float
    _trigger_key: int
    _auto_thread: threading.Thread | None
    _running: bool

    def __init__(self, trigger_key: int = 4):
        self.response_queue = deque()
        self._device_queue = deque()
        self._start_time = time.time()

        self._trigger_key = trigger_key

        self._auto_thread = None
        self._running = False

    # ------------------------
    # Core pyxid2 API
    # ------------------------

    def poll_for_response(self) -> None:
        """Move one event from device queue to response_queue."""
        if self._device_queue:
            self.response_queue.append(self._device_queue.popleft())

    def get_next_response(self) -> XidEvent:
        return self.response_queue.popleft()

    def clear_response_queue(self) -> None:
        self.response_queue.clear()

    def response_queue_size(self):
        return len(self.response_queue)

    def reset_timer(self) -> None:
        self._start_time = time.time()

    # ------------------------
    # Simulation helpers
    # ------------------------

    def _emit(self, key: int, pressed: bool):
        timestamp = int((time.time() - self._start_time) * 1000)

        self._device_queue.append({
            "port": 0,
            "key": key,
            "pressed": pressed,
            "time": timestamp
        })

    def simulate_button(self, key: int):
        self._emit(key, True)
        self._emit(key, False)

    def simulate_trigger(self):
        self._emit(self._trigger_key, True)
        self._emit(self._trigger_key, False)

    # ------------------------
    # Auto trigger simulation
    # ------------------------

    def start_auto_trigger(self, interval: float = 2.0, initial_delay: float = 0.0) -> None:
        """
        Start background TR pulses.

        interval: seconds between triggers (TR)
        initial_delay: delay before first trigger (dummy scans)
        """
        if self._running:
            return

        self._running = True

        def loop():
            try:
                if initial_delay > 0:
                    time.sleep(initial_delay)

                while self._running:
                    self.simulate_trigger()

                    next_time = time.time() + interval
                    while self._running and time.time() < next_time:
                        time.sleep(0.001)

            except Exception as e:
                print(f"[MockPyXID] Auto-trigger thread error: {e}")

        self._auto_thread = threading.Thread(target=loop, daemon=True)
        self._auto_thread.start()

    def stop_auto_trigger(self) -> None:
        self._running = False

        if self._auto_thread is not None:
            self._auto_thread.join()
            self._auto_thread = None



# class MockXIDDevice:
#     def __init__(self, trigger_key=4):
#         self.buffer = queue.Queue()
#         self.start_time = time.time()
#         self.trigger_key = trigger_key
# 
#         # Auto-trigger control
#         self._auto_thread = None
#         self._running = False
# 
#     # ------------------------
#     # D2XX-like API
#     # ------------------------
# 
#     def read(self, n=6):
#         data = bytearray()
# 
#         while len(data) < n:
#             try:
#                 data.extend(self.buffer.get_nowait())
#             except queue.Empty:
#                 break
# 
#         if data:
#             print(f"[MockXID] {list(data)}")
# 
#         return bytes(data)
# 
#     def write(self, data: bytes):
#         if b'e' in data:
#             self.start_time = time.time()
# 
#     # ------------------------
#     # Manual simulation
#     # ------------------------
# 
#     def simulate_trigger(self):
#         """Simulate one scanner pulse."""
#         self._emit_keypress(self.trigger_key, pressed=True)
#         self._emit_keypress(self.trigger_key, pressed=False)
# 
#     def simulate_button(self, button: int, delay: float = 0.0):
#         """Simulate participant response."""
#         self._emit_keypress(button, pressed=True)
# 
#         if delay > 0:
#             time.sleep(delay)
# 
#         self._emit_keypress(button, pressed=False)
# 
#     def _emit_keypress(self, button: int, *, port: int = 0, pressed: bool = True):
#         timestamp = int(time.time() - self.start_time) * 1000
# 
#         key_info = (
#             (button << 5) |
#             ((1 if pressed else 0) << 4) |
#             (port & 0x0F)
#         )
# 
#         packet = bytearray([
#             ord('k'),
#             key_info,
#             timestamp & 0xFF,
#             (timestamp >> 8) & 0xFF,
#             (timestamp >> 16) & 0xFF,
#             (timestamp >> 24) & 0xFF,
#         ])
# 
#         self.buffer.put(packet)
# 
#     # ------------------------
#     # Auto TR simulation
#     # ------------------------
# 
#     def start_auto_trigger(self, interval=1.0, initial_delay=0.0):
#         """
#         Start background TR pulses.
# 
#         interval: seconds between triggers (TR)
#         initial_delay: delay before first trigger (dummy scans)
#         """
#         if self._running:
#             return
# 
#         self._running = True
# 
#         def loop():
#             if initial_delay > 0:
#                 time.sleep(initial_delay)
# 
#             while self._running:
#                 time.sleep(interval)
#                 self.simulate_trigger()
# 
#         self._auto_thread = threading.Thread(target=loop, daemon=True)
#         self._auto_thread.start()
# 
#     def stop_auto_trigger(self):
#         self._running = False
