from __future__ import annotations

from dataclasses import dataclass
import math

Pos = tuple[float, float]

DEFAULT_RADIUS: float = 0.4
DEFAULT_START_ANGLE_RADIANS: float = 0.0
DEFAULT_CENTER_POS: Pos = (0.0, 0.0)


@dataclass(frozen=True)
class RingLayoutConfig:
    radius: float = DEFAULT_RADIUS
    start_angle_radians: float = DEFAULT_START_ANGLE_RADIANS
    center: Pos = DEFAULT_CENTER_POS


@dataclass(frozen=True)
class RingLayout:
    n_slots: int
    radius: float = DEFAULT_RADIUS
    start_angle_radians: float = 0.0
    center: Pos = (0.0, 0.0)

    @classmethod
    def from_config(cls, *, n_slots: int, config: RingLayoutConfig) -> RingLayout:
        return cls(
            n_slots=n_slots,
            radius=config.radius,
            start_angle_radians=config.start_angle_radians,
            center=config.center
        )

    @property
    def positions(self) -> list[Pos]:
        cx, cy = self.center
        return [
            (
                cx + self.radius * math.cos(
                    self.start_angle_radians + ((2 * math.pi * i) / self.n_slots)
                ),
                cy + self.radius * math.sin(
                    self.start_angle_radians + ((2 * math.pi * i) / self.n_slots)
                ),
            )
            for i in range(self.n_slots)
        ]


