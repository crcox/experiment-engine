from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class DisplayProfile:
    width: int
    height: int
    fullscr: bool
    name: str
    units: str = "height"
    color: str = "grey" # (0.00392156862745097, 0.00392156862745097, 0.00392156862745097)
    colorSpace: str = "rgb"

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def to_dict(self):
        asdict(self)


SCANNER_DISPLAY = DisplayProfile(
    width=800,
    height=600,
    fullscr=True,
    name="scanner"
)

SCANNER_DEBUG = DisplayProfile(
    width=800,
    height=600,
    fullscr=False,
    name="scanner-debug"
)

LAPTOP_DISPLAY = DisplayProfile(
    width=1920,
    height=1200,
    fullscr=True,
    name="laptop"
)

NULL_DISPLAY = DisplayProfile(
    width=0,
    height=0,
    fullscr=False,
    name="null"
)
