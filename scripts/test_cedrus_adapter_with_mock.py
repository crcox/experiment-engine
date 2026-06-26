from pathlib import Path
from mcj.config.paths import paths
from mcj.adapters.pyxid2.mock import MockXidDevice
from mcj.runtime.cedrus import CedrusAdapter
import time


def main():
    paths.initialize(
        root=Path.cwd(),
    )
    paths.add_ftd2xx_dll_directory()

    mock = MockXidDevice(trigger_key=4)
    adapter = CedrusAdapter(device=mock, trigger_key=4)
    time.sleep(.01)

    # Section 1: Adapter correctness
    ## 1.1 Single button press
    mock.simulate_button(1)
    events = adapter.update()
    assert(len(events) == 2)
    assert(events[0].is_press)
    assert(not events[1].is_press)

    print("  1.1 Single button press")
    for i,event in enumerate(events):
        print(i, event)

    ## 1.2 Single trigger signal 
    mock.simulate_trigger()
    events = adapter.update()
    assert(len(events) == 2)
    assert(events[0].is_press)
    assert(not events[1].is_press)

    print("  1.2 Single trigger signal")
    for i,event in enumerate(events):
        print(i, event)

    ## 1.3 Mixed inputs
    mock.simulate_button(1)
    mock.simulate_trigger()
    mock.simulate_button(2)
    events = adapter.update()
    assert(len(events) == 6)

    print("  1.3 Mixed inputs")
    for i,event in enumerate(events):
        print(i, event)

    # Section 2: Queue behavior
    ## 2.1 Multiple events (already checked above with mixed input)

    ## 2.2 Partial polling behavior
    ## Nothing has been added since the previous poll(), so this should return
    ## nothing.
    events = adapter.update()
    print("  2.2 Empty queue")
    print(events)

    ## 2.3 Queue clearing
    mock.simulate_button(3)
    mock.simulate_trigger()
    mock.simulate_button(2)
    adapter.clear()
    events = adapter.update()
    print("  2.3 Clear queue")
    print(events)

if __name__ == "__main__":
    main()
