from mcj.xid.mock import MockXIDDevice

class XIDInterface:
    def __init__(self, backend="mock"):
        if backend == "mock":
            self.dev = MockXIDDevice(auto_trigger=False)
        elif backend == "real":
            import ftd2xx
            self.dev = ftd2xx.open(0)
        else:
            raise ValueError("Unknown backend")

    def read(self, n=7):
        return self.dev.read(n)

    def write(self, data):
        self.dev.write(data)

    # Debug helpers (mock only)
    def simulate_trigger(self):
        if hasattr(self.dev, "simulate_trigger"):
            self.dev.simulate_trigger()
