import time
import queue
import threading


class MockXIDDevice:
    def __init__(self, trigger_key=5):
        self.buffer = queue.Queue()
        self.start_time = time.time()
        self.trigger_key = trigger_key

        # Auto-trigger control
        self._auto_thread = None
        self._running = False

    # ------------------------
    # D2XX-like API
    # ------------------------

    def read(self, n=7):
        data = bytearray()

        while len(data) < n:
            try:
                data.extend(self.buffer.get_nowait())
            except queue.Empty:
                break

        if data:
            print(f"[MockXID] {list(data)}")

        return bytes(data)

    def write(self, data: bytes):
        if b'e' in data:
            self.start_time = time.time()

    # ------------------------
    # Manual simulation
    # ------------------------

    def simulate_trigger(self):
        """Simulate one scanner pulse."""
        self._emit_keypress(self.trigger_key)

    def simulate_button(self, key):
        """Simulate participant response."""
        self._emit_keypress(key)

    def _emit_keypress(self, key):
        timestamp = int((time.time() - self.start_time) * 1000)

        packet = bytearray([
            ord('k'),
            key,
            0,
            timestamp & 0xFF,
            (timestamp >> 8) & 0xFF,
            (timestamp >> 16) & 0xFF,
            (timestamp >> 24) & 0xFF,
        ])

        self.buffer.put(packet)

    # ------------------------
    # Auto TR simulation
    # ------------------------

    def start_auto_trigger(self, interval=1.0, initial_delay=0.0):
        """
        Start background TR pulses.

        interval: seconds between triggers (TR)
        initial_delay: delay before first trigger (dummy scans)
        """
        if self._running:
            return

        self._running = True

        def loop():
            if initial_delay > 0:
                time.sleep(initial_delay)

            while self._running:
                time.sleep(interval)
                self.simulate_trigger()

        self._auto_thread = threading.Thread(target=loop, daemon=True)
        self._auto_thread.start()

    def stop_auto_trigger(self):
        self._running = False
