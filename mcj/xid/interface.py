from mcj.xid.mock import MockXidDevice

class XidInterface:
    def __init__(self, backend: str="mock"):
        if backend == "mock":
            self.dev = MockXidDevice()
        elif backend == "real":
            import ftd2xx
            self.dev = ftd2xx.open(0)
        else:
            raise ValueError("Unknown backend")

    def read(self, n: int=7):
        return self.dev.read(n)

    def write(self, data):
        self.dev.write(data)

    # Debug helpers (mock only)
    def simulate_trigger(self):
        if isinstance(self.dev, MockXidDevice):
            self.dev.simulate_trigger()
