"""Shared XP3312 circular pin geometry (datasheet / Prutchi Fig. 4).

Pin view = looking at the tube base (pins facing you). Short pin SP at south;
numbered pins 1..19 proceed clockwise. 20 positions at 18° spacing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Datasheet XP3312 flying-lead pin circle diameter 31.8 mm
FP_PIN_CIRCLE_DIA_MM = 31.8
FP_PIN_DIA_MM = 1.2
FP_DRILL_MM = 1.3
FP_PAD_DIA_MM = 2.4
FP_GUIDE_DIA_MM = 9.5  # center index max

# Schematic symbol uses a larger circle so names remain readable
SCH_PIN_CIRCLE_R_MM = 22.86  # 9 * 2.54
SCH_PIN_LEN_MM = 2.54

# Electrode map (Prutchi Fig. 4 / Photonis outline)
ELECTRODES: dict[int | str, str] = {
    "SP": "SP",
    1: "D1",
    2: "ic",
    3: "D2",
    4: "D3",
    5: "ic",
    6: "ic",
    7: "D4",
    8: "D5",
    9: "D6",
    10: "D7",
    11: "D8",
    12: "A",
    13: "ic",
    14: "ic",
    15: "ic",
    16: "K",
    17: "ic",
    18: "ic",
    19: "ic",
}

ACTIVE = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "A", "K"}


@dataclass(frozen=True)
class PinPos:
    number: str  # "SP" or "1".."19"
    name: str
    angle_deg: float  # math angle, 0=+X, CCW; pin faces outward along this angle
    x: float
    y: float

    @property
    def is_active(self) -> bool:
        return self.name in ACTIVE


def _angle_for_index(index: int) -> float:
    """Index 0 = SP at south (270°); then clockwise → decreasing math angle."""
    return 270.0 - index * 18.0


def pin_positions(radius: float) -> list[PinPos]:
    """Return SP + pins 1..19 on a circle of the given radius (mm)."""
    order: list[int | str] = ["SP", *range(1, 20)]
    out: list[PinPos] = []
    for i, key in enumerate(order):
        ang = _angle_for_index(i)
        rad = math.radians(ang)
        name = ELECTRODES[key]
        num = str(key)
        out.append(
            PinPos(
                number=num,
                name=name,
                angle_deg=ang,
                x=round(radius * math.cos(rad), 4),
                y=round(radius * math.sin(rad), 4),
            )
        )
    return out


def outward_pin_angle(angle_deg: float) -> int:
    """KiCad schematic pin orientation snapped to 0/90/180/270.

    Tips may sit anywhere on the circle; KiCad pin *orientation* must be
    cardinal (arbitrary angles fail to load). Pick the nearest outward axis.
    """
    a = angle_deg % 360
    return int(round(a / 90.0) * 90) % 360
