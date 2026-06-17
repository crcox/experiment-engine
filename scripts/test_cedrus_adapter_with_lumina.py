
from pathlib import Path

from psychopy.clock import monotonicClock

from mcj.config.paths import paths
from mcj.runtime.cedrus import CedrusAdapter
from mcj.runtime.synchronization import sync_cedrus_and_experiment_clocks_testing


def main():
    paths.initialize(
        root=Path.cwd(),
        subject_id=1000
    )
    paths.add_ftd2xx_dll_directory()

    adapter = CedrusAdapter(trigger_key=4)

    sync_cedrus_and_experiment_clocks_testing(adapter, monotonicClock.getTime)





if __name__ == "__main__":
    main()
