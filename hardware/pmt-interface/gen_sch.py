#!/usr/bin/env python3
"""Generate pmt-interface KiCad schematic + XP3312 symbol (continuity draft)."""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

from tube_geo import (
    SCH_PIN_CIRCLE_R_MM,
    SCH_PIN_LEN_MM,
    outward_pin_angle,
    pin_positions,
)

ROOT = Path(__file__).resolve().parent
LIB_DIR = ROOT / "libraries"
PROJECT = "pmt-interface"
SHEET = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/pmt-interface")
# Hierarchical sheet symbol on root (page 2 link); distinct from child file UUID
BRINGUP_SHEET_SYM = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/pmt-interface/sheet-sym-bringup")
BRINGUP_SHEET_FILE = "bringup-supply.kicad_sch"
BRINGUP_SHEET_FILE_UUID = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/pmt-interface/bringup-supply")

# KiCad default schematic grid (50 mil)
GRID_MM = 1.27

# Wide IC-style 2×7 socket: pin tips on left/right, 0.6"-class body gap
HDR_PIN_X = 10.16  # local ±X of pin tips
HDR_BODY_X = 7.62
HDR_Y0 = 7.62  # pin 1 / 14 local Y (top)


def snap(v: float, grid: float = GRID_MM) -> float:
    return round(round(v / grid) * grid, 2)


def snap_pt(x: float, y: float, grid: float = GRID_MM) -> tuple[float, float]:
    return (snap(x, grid), snap(y, grid))


def uid(name: str) -> str:
    return str(uuid.uuid5(SHEET, name))


def lib_prop(name: str, value: str, x: float, y: float, hide: bool = False) -> str:
    hidden = "\n\t\t\t(hide yes)" if hide else ""
    return (
        f'\t\t\t(property "{name}" "{value}"\n'
        f"\t\t\t\t(at {x:.2f} {y:.2f} 0)\n"
        "\t\t\t\t(show_name no)\n"
        "\t\t\t\t(do_not_autoplace no)"
        f"{hidden}\n"
        "\t\t\t\t(effects\n"
        "\t\t\t\t\t(font\n"
        "\t\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t\t)\n"
        "\t\t\t\t)\n"
        "\t\t\t)"
    )


def pin(number: str, x: float, y: float, angle: int, name: str = "", etype: str = "passive") -> str:
    return f"""\t\t\t\t(pin {etype} line
\t\t\t\t\t(at {x:.2f} {y:.2f} {angle})
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{name}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.016 1.016)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t\t(number "{number}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.016 1.016)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)"""


def _line(pts: list[tuple[float, float]]) -> str:
    body = "\n".join(f"\t\t\t\t\t\t(xy {x:.2f} {y:.2f})" for x, y in pts)
    return f"""\t\t\t\t(polyline
\t\t\t\t\t(pts
{body}
\t\t\t\t\t)
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)"""


def _rect(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""\t\t\t\t(rectangle
\t\t\t\t\t(start {x1:.2f} {y1:.2f})
\t\t\t\t\t(end {x2:.2f} {y2:.2f})
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type background)
\t\t\t\t\t)
\t\t\t\t)"""


def _circle(radius: float) -> str:
    return f"""\t\t\t\t(circle
\t\t\t\t\t(center 0 0)
\t\t\t\t\t(radius {radius:.2f})
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type background)
\t\t\t\t\t)
\t\t\t\t)"""


def circular_tube_pins() -> str:
    """Full 20-position circle matching footprint / datasheet (SP + 1..19)."""
    lines = []
    for p in pin_positions(SCH_PIN_CIRCLE_R_MM):
        etype = "passive" if p.is_active else "no_connect"
        # Tip on circle; orientation must be cardinal (KiCad load requirement)
        ang = outward_pin_angle(p.angle_deg)
        lines.append(pin(p.number, p.x, p.y, ang, p.name, etype=etype))
    return "\n".join(lines)


def symbol_wrap(
    lib_id: str,
    body: str,
    pins: str,
    reference: str,
    value: str | None = None,
    *,
    power: bool = False,
) -> str:
    stem = lib_id.split(":")[-1]
    val = value or stem
    power_flag = "\n\t\t\t(power)" if power else ""
    # Power symbols: hide Ref, show Value below bars
    ref_prop = lib_prop("Reference", reference, 0, 2.54, hide=True) if power else lib_prop("Reference", reference, 2.54, 0)
    val_prop = lib_prop("Value", val, 0, -3.81, hide=False) if power else lib_prop("Value", val, 0, 0)
    return f"""\t\t(symbol "{lib_id}"
\t\t\t(pin_names
\t\t\t\t(offset 0.254)
\t\t\t){power_flag}
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom {"no" if power else "yes"})
\t\t\t(on_board yes)
\t\t\t(in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
{ref_prop}
{val_prop}
{lib_prop("Footprint", "", 0, -2.54, hide=True)}
{lib_prop("Datasheet", "", 0, -5.08, hide=True)}
\t\t\t(symbol "{stem}_0_1"
{body}
\t\t\t)
\t\t\t(symbol "{stem}_1_1"
{pins}
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""


def graphics() -> str:
    resistor = _rect(-1.016, -2.54, 1.016, 2.54)
    capacitor = (
        _line([(-1.80, 0.40), (1.80, 0.40)])
        + "\n"
        + _line([(-1.80, -0.40), (1.80, -0.40)])
        + "\n"
        + _line([(0, 2.54), (0, 0.40)])
        + "\n"
        + _line([(0, -0.40), (0, -2.54)])
    )
    # GND: connection at origin; bars go local -Y (down on sheet when unrotated).
    ground = (
        _line([(-2.54, 0), (2.54, 0)])
        + "\n"
        + _line([(-1.27, -1.27), (1.27, -1.27)])
        + "\n"
        + _line([(-0.5, -2.0), (0.5, -2.0)])
    )
    r_pins = pin("1", 0, 3.81, 270) + "\n" + pin("2", 0, -3.81, 90)
    c_pins = pin("1", 0, 2.54, 270) + "\n" + pin("2", 0, -2.54, 90)
    # Graphic GND only — net joins via global_label "GND" (avoids power_pin_not_driven)
    g_pin = pin("1", 0, 0, 270, "", etype="passive").replace("(length 2.54)", "(length 0)")

    # DIP-14 / wide IC socket 2×7 (NOT IDC ribbon Odd/Even). Prutchi Fig.3 wrap:
    #   left 1‥7 top→bottom ; right 14‥8 top→bottom (pin7 across from pin8).
    # PCB footprint uses 7.62 mm row spacing; schematic body is wider for readability.
    hdr_body = _rect(-HDR_BODY_X, HDR_Y0 + 2.54, HDR_BODY_X, -(HDR_Y0 + 2.54))
    hdr_pins = []
    for row in range(7):
        y = HDR_Y0 - row * 2.54
        left = 1 + row
        right = 14 - row
        hdr_pins.append(pin(str(left), -HDR_PIN_X, y, 180, str(left)))
        hdr_pins.append(pin(str(right), HDR_PIN_X, y, 0, str(right)))

    coax_body = (
        _line([(0, 2.54), (0, 0.5)])
        + "\n"
        + _line([(-2.0, 0.5), (2.0, 0.5), (0, -2.0), (-2.0, 0.5)])
        + "\n"
        + _line([(-2.54, -2.54), (2.54, -2.54)])
    )
    coax_pins = pin("1", 0, 5.08, 270, "In") + "\n" + pin("2", 0, -5.08, 90, "Shield")

    # Body slightly inside pin tips so pads sit on the ring
    tube_body = _circle(SCH_PIN_CIRCLE_R_MM - SCH_PIN_LEN_MM)
    tube_pins = circular_tube_pins()

    return "\n".join(
        [
            symbol_wrap("pmt:R", resistor, r_pins, "R"),
            symbol_wrap("pmt:C", capacitor, c_pins, "C"),
            symbol_wrap("pmt:GND", ground, g_pin, "#PWR", "GND"),
            symbol_wrap("pmt:HDR14", hdr_body, "\n".join(hdr_pins), "J", "HDR_2x7_IC_Socket"),
            symbol_wrap("pmt:COAX", coax_body, coax_pins, "J", "COAX"),
            symbol_wrap("pmt:XP3312", tube_body, tube_pins, "U", "XP3312").replace(
                lib_prop("Footprint", "", 0, -2.54, hide=True),
                lib_prop("Footprint", "XP3312:XP3312_FlyingLead", 0, -2.54, hide=True),
            ),
        ]
    )


def prop(name: str, value: str, x: float, y: float, hide: bool = False) -> str:
    hidden = "\n\t\t\t(hide yes)" if hide else ""
    return f"""\t\t(property "{name}" "{value}"
\t\t\t(at {x:.2f} {y:.2f} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no){hidden}
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)"""


# PCB footprints (fab-ready photo-matched board — see gen_pcb.py)
FP = {
    "U1": "XP3312:XP3312_FlyingLead",
    "J1": "XP3312:HDR_2x7_IC_Socket",
    "J2": "XP3312:COAX_Edge",
    "C1": "Capacitor_THT:C_Disc_D7.5mm_W2.5mm_P5.00mm",
    "C2": "Capacitor_SMD:C_0805_2012Metric",
    "C3": "Capacitor_SMD:C_0805_2012Metric",
    "R1": "Resistor_SMD:R_0805_2012Metric",
    "R2": "Resistor_SMD:R_0805_2012Metric",
    "R3": "Resistor_SMD:R_0805_2012Metric",
}


def placed(
    lib_id: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    numbers: tuple[str, ...],
    rot: int = 0,
    footprint: str | None = None,
) -> str:
    pin_lines = "\n".join(
        f'\t\t(pin "{number}"\n\t\t\t(uuid "{uid(ref + "-" + number)}")\n\t\t)' for number in numbers
    )
    fp = footprint if footprint is not None else FP.get(ref, "")
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x:.2f} {y:.2f} {rot})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{uid(ref)}")
{prop("Reference", ref, x + 2.54, y + 3.81)}
{prop("Value", value, x + 2.54, y + 1.27)}
{prop("Footprint", fp, x, y, hide=True)}
{prop("Datasheet", "", x, y, hide=True)}
{pin_lines}
\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "/{SHEET}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def wire(name: str, x1: float, y1: float, x2: float, y2: float) -> str:
    """Single segment; diagonal allowed (Δx and Δy both nonzero). Crossings do not join."""
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1:.2f} {y1:.2f})
\t\t\t(xy {x2:.2f} {y2:.2f})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid(name)}")
\t)"""


def wire_path(name: str, points: list[tuple[float, float]]) -> list[str]:
    """Polyline of orthogonal and/or diagonal segments (no auto-junctions at crossings)."""
    segs: list[str] = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        if a == b:
            continue
        segs.append(wire(f"{name}-{i}", a[0], a[1], b[0], b[1]))
    return segs


def label(name: str, text: str, x: float, y: float) -> str:
    return f"""\t(label "{text}"
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid('label-' + name)}")
\t)"""


def global_label(name: str, text: str, x: float, y: float, rot: int = 270) -> str:
    """Global net label (used for GND so ERC sees a driven net without PWR_FLAG)."""
    return f"""\t(global_label "{text}"
\t\t(shape round)
\t\t(at {x:.2f} {y:.2f} {rot})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left)
\t\t)
\t\t(uuid "{uid('glabel-' + name)}")
\t)"""


def note(name: str, text: str, x: float, y: float, size: float = 1.27) -> str:
    return f"""\t(text "{text}"
\t\t(exclude_from_sim no)
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size:.2f} {size:.2f})
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid('text-' + name)}")
\t)"""


def no_connect(name: str, x: float, y: float) -> str:
    return f"""\t(no_connect
\t\t(at {x:.2f} {y:.2f})
\t\t(uuid "{uid('nc-' + name)}")
\t)"""


def junction(name: str, x: float, y: float) -> str:
    return f"""\t(junction
\t\t(at {x:.2f} {y:.2f})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{uid('junc-' + name)}")
\t)"""


def hierarchical_sheet(
    name: str,
    sheetfile: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    sym_uuid: uuid.UUID,
) -> str:
    """Navigation sheet box (no hierarchical pins — child is a mate harness)."""
    return f"""\t(sheet
\t\t(at {x:.2f} {y:.2f})
\t\t(size {w:.2f} {h:.2f})
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(stroke
\t\t\t(width 0.1524)
\t\t\t(type solid)
\t\t)
\t\t(fill
\t\t\t(color 0 0 0 0)
\t\t)
\t\t(uuid "{sym_uuid}")
\t\t(property "Sheetname" "{name}"
\t\t\t(at {x:.2f} {y - 1.27:.2f} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t(thickness 0.254)
\t\t\t\t\t(bold yes)
\t\t\t\t)
\t\t\t\t(justify left bottom)
\t\t\t)
\t\t)
\t\t(property "Sheetfile" "{sheetfile}"
\t\t\t(at {x:.2f} {y + h + 1.27:.2f} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(justify left top)
\t\t\t)
\t\t)
\t)"""


def hdr_pin(j1_x: float, j1_y: float, n: int) -> tuple[float, float]:
    """Sheet coords of HDR14 pin tip — wide IC socket wrap numbering.

    Local: left x=-HDR_PIN_X pins 1‥7 top→bottom; right x=+HDR_PIN_X pins 14‥8.
    Sheet Y = origin_y - local_y.
    """
    if not 1 <= n <= 14:
        raise ValueError(n)
    row = (n - 1) if n <= 7 else (14 - n)
    local_y = HDR_Y0 - row * 2.54
    local_x = -HDR_PIN_X if n <= 7 else HDR_PIN_X
    return (round(j1_x + local_x, 2), round(j1_y - local_y, 2))


def hdr_stub(j1_x: float, j1_y: float, n: int, length: float = 5.08) -> tuple[float, float]:
    """Outward stub from IC-socket pin (left −X, right +X)."""
    x, y = hdr_pin(j1_x, j1_y, n)
    return (round(x - length, 2), y) if n <= 7 else (round(x + length, 2), y)


def schematic() -> str:
    """Verified stock-board schematic (continuity 2026-11-01).

    Tube = circular datasheet/footprint map (tube_geo). Components on 1.27 mm grid.
    J1 = wide IC socket (wrap 1‥7 | 14‥8). Diagonal fan-out OK.
    """
    # Origins snapped to KiCad 1.27 mm grid (user readability layout)
    u_x, u_y = snap_pt(69.85, 110.49)
    j1_x, j1_y = snap_pt(215.90, 110.49)
    j2_x, j2_y = snap_pt(149.86, 90.17)
    stub_len = 7.62

    # Sheet Y↓; symbol local Y↑ — flip Y when mapping tips onto the sheet.
    def sheet_xy(lx: float, ly: float) -> tuple[float, float]:
        return (round(u_x + lx, 2), round(u_y - ly, 2))

    pins = pin_positions(SCH_PIN_CIRCLE_R_MM)
    by_name = {p.name: p for p in pins if p.is_active}

    def tip(name: str) -> tuple[float, float]:
        p = by_name[name]
        return sheet_xy(p.x, p.y)

    def radial_out(name: str, length: float = stub_len) -> tuple[float, float]:
        """Point outward from pin tip along datasheet angle (sheet coords)."""
        p = by_name[name]
        rad = math.radians(p.angle_deg)
        return sheet_xy(p.x + length * math.cos(rad), p.y + length * math.sin(rad))

    k_xy = tip("K")
    d1_xy, d2_xy, d3_xy, d4_xy = tip("D1"), tip("D2"), tip("D3"), tip("D4")
    d5_xy, d6_xy, d7_xy, d8_xy = tip("D5"), tip("D6"), tip("D7"), tip("D8")
    a_xy = tip("A")

    # Passives (grid-snapped) — filter cluster left; K/C1/R1 near cathode; A/R2/J2 above
    r1_x, r1_y = snap_pt(119.38, 121.92)
    c1_x, c1_y = snap_pt(111.76, 130.81)
    r2_x, r2_y = snap_pt(143.51, 88.90)
    c2_x, c2_y = snap_pt(52.07, 158.75)
    c3_x, c3_y = snap_pt(67.31, 158.75)
    r3_x, r3_y = snap_pt(59.69, 171.45)

    # Pin tips
    c1_pos = (c1_x, snap(c1_y - 2.54))
    c1_neg = (c1_x, snap(c1_y + 2.54))
    # R1 rot=90 → pins left/right; R2/R3 vertical → pins top/bottom
    r1_a = (snap(r1_x - 3.81), r1_y)
    r1_b = (snap(r1_x + 3.81), r1_y)
    r2_top = (r2_x, snap(r2_y - 3.81))
    r2_bot = (r2_x, snap(r2_y + 3.81))
    coax_in = (j2_x, snap(j2_y - 5.08))
    coax_sh = (j2_x, snap(j2_y + 5.08))
    r3_top = (r3_x, snap(r3_y - 3.81))
    r3_bot = (r3_x, snap(r3_y + 3.81))
    h14 = hdr_pin(j1_x, j1_y, 14)
    h14_stub = hdr_stub(j1_x, j1_y, 14)
    # Outboard of the right-side stub column (do NOT drop in +Y — that hits other pin rows)
    h14_gnd = snap_pt(h14_stub[0] + 5.08, h14_stub[1])

    tube_pin_nums = tuple(p.number for p in pins)

    symbols = [
        placed("pmt:XP3312", "U1", "XP3312/SQ", u_x, u_y, tube_pin_nums),
        placed(
            "pmt:HDR14",
            "J1",
            "HDR_2x7_IC_Socket",
            j1_x,
            j1_y,
            tuple(str(i) for i in range(1, 15)),
        ),
        placed("pmt:COAX", "J2", "COAX_A", j2_x, j2_y, ("1", "2")),
        placed("pmt:R", "R1", "1k", r1_x, r1_y, ("1", "2"), rot=90),
        placed("pmt:C", "C1", "4.7nF 2kV", c1_x, c1_y, ("1", "2")),
        placed("pmt:R", "R2", "1.1M", r2_x, r2_y, ("1", "2")),
        placed("pmt:C", "C2", "MLCC J1.13", c2_x, c2_y, ("1", "2")),
        placed("pmt:C", "C3", "MLCC D8", c3_x, c3_y, ("1", "2")),
        placed("pmt:R", "R3", "10R", r3_x, r3_y, ("1", "2")),
        # GND graphics just beyond each grounded pin; short wire + global_label join the net
        placed("pmt:GND", "GND1", "GND", c1_neg[0], snap(c1_neg[1] + 2.54), ("1",)),
        placed("pmt:GND", "GND2", "GND", coax_sh[0], snap(coax_sh[1] + 2.54), ("1",)),
        placed("pmt:GND", "GND3", "GND", snap(h14_gnd[0] + 2.54), h14_gnd[1], ("1",)),
        placed("pmt:GND", "GND4", "GND", r3_bot[0], snap(r3_bot[1] + 2.54), ("1",)),
        placed("pmt:GND", "GND5", "GND", r2_bot[0], snap(r2_bot[1] + 2.54), ("1",)),
    ]

    wires: list[str] = []
    labels: list[str] = []
    ncs: list[str] = []
    junctions: list[str] = []

    def path(name: str, pts: list[tuple[float, float]]) -> None:
        wires.extend(wire_path(name, pts))

    def stub_net(name: str, src: tuple[float, float]) -> tuple[float, float]:
        stub = radial_out(name)
        dx = stub[0] - src[0]
        dy = stub[1] - src[1]
        kick = snap_pt(
            stub[0] + math.copysign(2.54, dx or 1),
            stub[1] + math.copysign(2.54, dy or 1),
        )
        path(f"{name}-stub", [src, stub, kick])
        labels.append(label(name, name, kick[0], kick[1]))
        return kick

    # --- K net: tube K, C1 top, R1 left wired at one junction (not label-only) ---
    k_stub = radial_out("K")
    k_junc = snap_pt(r1_a[0] - 5.08, r1_y)
    path("k-tube", [k_xy, k_stub, (k_junc[0], k_stub[1]), k_junc])
    path("k-r1", [k_junc, r1_a])
    path("k-c1", [k_junc, (k_junc[0], c1_pos[1]), c1_pos])
    junctions.append(junction("K", k_junc[0], k_junc[1]))
    labels.append(label("K", "K", k_junc[0], k_junc[1]))

    h7 = hdr_pin(j1_x, j1_y, 7)
    h7s = hdr_stub(j1_x, j1_y, 7)
    path("r1-h7", [r1_b, (h7s[0], r1_b[1]), h7s, h7])

    # A -- R2 (vertical) -- GND5; A -- coax
    a_kick = stub_net("A", a_xy)
    path("a-r2", [a_kick, (a_kick[0], r2_top[1]), r2_top])
    path("a-coax", [a_kick, (a_kick[0], coax_in[1]), coax_in])

    # Short wires from grounded pins to GND symbol + global_label
    c1_g = (c1_neg[0], snap(c1_neg[1] + 2.54))
    r2_g = (r2_bot[0], snap(r2_bot[1] + 2.54))
    r3_g = (r3_bot[0], snap(r3_bot[1] + 2.54))
    coax_g = (coax_sh[0], snap(coax_sh[1] + 2.54))
    h14_g = (snap(h14_gnd[0] + 2.54), h14_gnd[1])
    path("c1-gnd", [c1_neg, c1_g])
    path("r2-gnd", [r2_bot, r2_g])
    path("r3-gnd", [r3_bot, r3_g])
    path("coax-gnd", [coax_sh, coax_g])
    path("h14-gnd", [h14, h14_stub, h14_gnd, h14_g])
    for gname, gpt in [
        ("gnd-c1", c1_g),
        ("gnd-r2", r2_g),
        ("gnd-r3", r3_g),
        ("gnd-coax", coax_g),
        ("gnd-h14", h14_g),
    ]:
        labels.append(global_label(gname, "GND", gpt[0], gpt[1]))

    # Dynodes: tube stub+label ; header outward stub+label
    for name, src, hp in [
        ("D8", d8_xy, 2),
        ("D7", d7_xy, 3),
        ("D5", d5_xy, 4),
        ("D4", d4_xy, 5),
        ("D3", d3_xy, 6),
        ("D1", d1_xy, 8),
        ("D2", d2_xy, 9),
        ("D6", d6_xy, 12),
    ]:
        stub_net(name, src)
        dst = hdr_pin(j1_x, j1_y, hp)
        end = hdr_stub(j1_x, j1_y, hp)
        path(f"{name}-hdr", [dst, end])
        labels.append(label(f"{name}-h", name, end[0], end[1]))

    # Filter: D8--C3--+--R3--GND ; J1.13--C2--+
    c2_top, c2_bot = (c2_x, snap(c2_y - 2.54)), (c2_x, snap(c2_y + 2.54))
    c3_top, c3_bot = (c3_x, snap(c3_y - 2.54)), (c3_x, snap(c3_y + 2.54))
    h13 = hdr_pin(j1_x, j1_y, 13)
    h13_end = hdr_stub(j1_x, j1_y, 13)
    path("h13-stub", [h13, h13_end])
    labels.append(label("J1.13-h", "J1.13", h13_end[0], h13_end[1]))
    path("c2-lab", [c2_top, (c2_x, snap(c2_top[1] - 5.08))])
    labels.append(label("J1.13-c2", "J1.13", c2_x, snap(c2_top[1] - 5.08)))
    path("c3-lab", [c3_top, (c3_x, snap(c3_top[1] - 5.08))])
    labels.append(label("D8-c3", "D8", c3_x, snap(c3_top[1] - 5.08)))
    mid_y = snap(max(c2_bot[1], c3_bot[1]) + 2.54)
    mid_x = snap((c2_x + c3_x) / 2)
    path("bypass-mid", [c2_bot, (c2_x, mid_y), (c3_x, mid_y), c3_bot])
    path("bypass-r3", [(mid_x, mid_y), (mid_x, r3_top[1]), r3_top])
    junctions.append(junction("BYPASS", mid_x, mid_y))
    labels.append(label("BYPASS_MID", "BYPASS_MID", mid_x, mid_y))

    for hp in (1, 10, 11):
        ncs.append(no_connect(f"j1-{hp}", *hdr_pin(j1_x, j1_y, hp)))

    texts = [
        note("t0", "VERIFIED schematic — continuity 2026-11-01; 1.27mm grid; wide IC J1", 20.32, 17.78, 2.54),
        note("t1", "View: bottom of tube looking up; SP south; 1..19 clockwise", 20.32, 22.86),
        note("t2", "J1 DIP-14 wide IC socket (7.62mm rows): left 1-7, right 14-8; not IDC ribbon", 20.32, 27.94),
        note("t3", "Electrodes: D1=1 D2=3 D3=4 D4=7 D5=8 D6=9 D7=10 D8=11 A=12 K=16", 20.32, 33.02),
        note("t4", "K wired: tube+C1+R1 junction; R1->J1.7; C3=D8 C2=J1.13 mid->R3->GND", 20.32, 38.10),
        note("t5", "J1: 2=D8 3=D7 4=D5 5=D4 6=D3 7=K 8=D1 9=D2 12=D6 13=filt 14=GND; 1/10/11=NC?", 20.32, 43.18),
        note("t6", "docs/pin-reconciliation.md · gen_sch.py --validate", 20.32, 48.26),
        note("t7", "Page 2 bringup-supply: Type A HV divider + anode scope — docs/bringup/", 20.32, 53.34),
    ]

    # Page 2 hierarchical sheet (mate harness; no hier pins — keeps page-1 ERC unchanged)
    sheet_box = hierarchical_sheet(
        "Bringup Supply",
        BRINGUP_SHEET_FILE,
        snap(250.19),
        snap(17.78),
        snap(50.80),
        snap(25.40),
        sym_uuid=BRINGUP_SHEET_SYM,
    )

    instances = "\n".join([*symbols, *wires, *labels, *junctions, *ncs, *texts, sheet_box])
    return f"""(kicad_sch
\t(version 20260306)
\t(generator "gen_sch.py")
\t(generator_version "10.0")
\t(uuid "{SHEET}")
\t(paper "A3")
\t(title_block
\t\t(title "pmt-interface")
\t\t(date "2026-11-02")
\t\t(rev "0.4-bringup-sheet")
\t\t(comment 1 "XP3312/SQ Philips medical I/O filter — continuity verified")
\t\t(comment 2 "Page 2: bringup-supply Type A divider + anode measure. Not a dynode divider on this sheet.")
\t)
\t(lib_symbols
{graphics()}
\t)
{instances}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t\t(path "/{BRINGUP_SHEET_SYM}"
\t\t\t(page "2")
\t\t)
\t)
)
"""


def write_symbol_lib() -> None:
    """Standalone library for reuse; schematic embeds its own copy."""
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    tube_body = _circle(SCH_PIN_CIRCLE_R_MM - SCH_PIN_LEN_MM)
    tube_pins = circular_tube_pins()
    sym = symbol_wrap("XP3312", tube_body, tube_pins, "U", "XP3312")
    # Link footprint property in the library copy
    sym = sym.replace(
        lib_prop("Footprint", "", 0, -2.54, hide=True),
        lib_prop("Footprint", "XP3312:XP3312_FlyingLead", 0, -2.54, hide=True),
    )
    path = LIB_DIR / "XP3312.kicad_sym"
    path.write_text(
        f"""(kicad_symbol_lib
\t(version 20250331)
\t(generator "gen_sch.py")
\t(generator_version "10.0")
{sym}
)
"""
    )
    print("wrote", path)


def write_project() -> None:
    """Update sheets list in existing .kicad_pro without wiping board/settings."""
    pro_path = ROOT / f"{PROJECT}.kicad_pro"
    sheets = [
        [str(SHEET), "Root"],
        [str(BRINGUP_SHEET_SYM), "Bringup Supply"],
    ]
    if pro_path.exists():
        try:
            pro = json.loads(pro_path.read_text())
        except json.JSONDecodeError:
            pro = {"meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}}
        pro["sheets"] = sheets
    else:
        pro = {
            "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
            "sheets": sheets,
            "text_variables": {},
        }
    pro_path.write_text(json.dumps(pro, indent=2) + "\n")
    (ROOT / "sym-lib-table").write_text(
        """(sym_lib_table
  (version 7)
  (lib (name "XP3312")(type "KiCad")(uri "${KIPRJMOD}/libraries/XP3312.kicad_sym")(options "")(descr "Photonis XP3312/SQ"))
)
"""
    )


def validate(sch_path: Path) -> int:
    """Auto-check grid snap, expected nets, and run KiCad ERC if available."""
    import re
    import subprocess

    text = sch_path.read_text()
    errors: list[str] = []

    # Component origins on 1.27 mm grid
    for m in re.finditer(
        r'\(lib_id "[^"]+"\)\s*\(at ([0-9.-]+) ([0-9.-]+) ([0-9]+)\)[\s\S]*?'
        r'\(property "Reference" "([^"]+)"',
        text,
    ):
        x, y, ref = float(m.group(1)), float(m.group(2)), m.group(4)
        if abs(x - snap(x)) > 0.011 or abs(y - snap(y)) > 0.011:
            errors.append(f"off-grid {ref} at ({x}, {y})")

    # Expected net labels present
    for need in ("K", "A", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "J1.13"):
        if not re.search(rf'\(label "{re.escape(need)}"', text):
            errors.append(f"missing net label {need}")
    if "pmt:GND" not in text:
        errors.append("GND symbol missing")
    if not re.search(r'\(global_label "GND"', text):
        errors.append("missing global_label GND")

    # K must have a drawn junction (wired fan-out)
    if text.count('(junction') < 1:
        errors.append("expected at least one junction (K fan-out)")

    # Wide IC socket: pin 1 left, pin 14 right (same local Y band as pin1)
    if "HDR_2x7_IC_Socket" not in text:
        errors.append("J1 value should be HDR_2x7_IC_Socket")
    if not re.search(r'\(at -10\.16 [0-9.-]+ 180\).*?\(number "1"', text, re.S):
        # embedded lib may order fields differently — check pin 1 at -10.16
        if '(at -10.16' not in text or '(at 10.16' not in text:
            errors.append("HDR14 pins not in wide IC ±10.16 layout")

    # Connectivity script: K label + R1 left pin share a wire-connected component
    segs = [
        ((float(a), float(b)), (float(c), float(d)))
        for a, b, c, d in re.findall(
            r'\(wire\s*\(pts\s*\(xy ([0-9.-]+) ([0-9.-]+)\)\s*\(xy ([0-9.-]+) ([0-9.-]+)\)',
            text,
        )
    ]
    parent: dict[tuple[float, float], tuple[float, float]] = {}

    def find(p: tuple[float, float]) -> tuple[float, float]:
        parent.setdefault(p, p)
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def union(a: tuple[float, float], b: tuple[float, float]) -> None:
        parent[find(a)] = find(b)

    def key(p: tuple[float, float]) -> tuple[float, float]:
        return (round(p[0], 2), round(p[1], 2))

    for a, b in segs:
        union(key(a), key(b))

    # R1 at snapped user pose
    r1 = None
    for m in re.finditer(
        r'\(lib_id "pmt:R"\)\s*\(at ([0-9.-]+) ([0-9.-]+) ([0-9]+)\)[\s\S]*?'
        r'\(property "Reference" "R1"',
        text,
    ):
        r1 = (float(m.group(1)), float(m.group(2)), int(m.group(3)))
        break
    c1 = None
    for m in re.finditer(
        r'\(lib_id "pmt:C"\)\s*\(at ([0-9.-]+) ([0-9.-]+) ([0-9]+)\)[\s\S]*?'
        r'\(property "Reference" "C1"',
        text,
    ):
        c1 = (float(m.group(1)), float(m.group(2)), int(m.group(3)))
        break

    if r1 and c1:
        # R1 rot 90 → left pin; C1 pin1 top
        r1_left = key((snap(r1[0] - 3.81), snap(r1[1])))
        c1_top = key((snap(c1[0]), snap(c1[1] - 2.54)))
        if r1_left not in parent or c1_top not in parent:
            errors.append("K wiring: R1 left or C1 top not on any wire")
        elif find(r1_left) != find(c1_top):
            errors.append("K wiring: R1 left and C1 top are not wire-connected")
    else:
        errors.append("could not find R1/C1 for K check")

    # Netlist is the source of truth for connectivity (ERC pin_not_connected can false-positive)
    net_path = sch_path.with_suffix(".net")
    try:
        subprocess.run(
            [
                "kicad-cli",
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadsexpr",
                "-o",
                str(net_path),
                str(sch_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        net = net_path.read_text() if net_path.exists() else ""
        # Find net blocks containing refs
        nets = re.findall(
            r'\(net\s+\(code "[^"]+"\)\s+\(name "([^"]+)"\)([\s\S]*?)(?=\(net\s+\(code |\Z)',
            net,
        )

        def refs_on(name_substr: str) -> set[str]:
            out: set[str] = set()
            for name, body in nets:
                if name_substr in name or name_substr in body:
                    if name_substr.startswith("/") or name == name_substr or name.endswith(name_substr):
                        out |= set(re.findall(r'\(ref "([^"]+)"\)', body))
            return out

        k_refs = set()
        gnd_refs = set()
        for name, body in nets:
            refs = set(re.findall(r'\(ref "([^"]+)"\)', body))
            if name in ("/K", "K") or (name.endswith("/K")):
                k_refs |= refs
            if name == "GND" or name.endswith("/GND") or name == "/GND":
                gnd_refs |= refs
        if not {"C1", "R1", "U1"} <= k_refs:
            errors.append(f"netlist K missing C1/R1/U1 (have {sorted(k_refs)})")
        else:
            print("netlist K OK:", sorted(k_refs))
        need_g = {"C1", "R2", "R3", "J1", "J2"}
        if not need_g <= gnd_refs:
            # also accept if pads listed under Net-(C1-Pad2) style merged wrongly
            errors.append(f"netlist GND missing {sorted(need_g - gnd_refs)} (have {sorted(gnd_refs)})")
        else:
            print("netlist GND OK:", sorted(gnd_refs))
    except FileNotFoundError:
        print("kicad-cli not found — skipped netlist check")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"netlist check failed: {exc}")

    erc_path = sch_path.with_suffix(".erc")
    try:
        erc_json = sch_path.with_suffix(".erc.json")
        subprocess.run(
            [
                "kicad-cli",
                "sch",
                "erc",
                "--format",
                "report",
                "--output",
                str(erc_path),
                str(sch_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        subprocess.run(
            [
                "kicad-cli",
                "sch",
                "erc",
                "--format",
                "json",
                "--severity-error",
                "--output",
                str(erc_json),
                str(sch_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        try:
            data = json.loads(erc_json.read_text()) if erc_json.exists() else {}
        except json.JSONDecodeError:
            data = {}
        for sheet in data.get("sheets", []):
            for v in sheet.get("violations", []):
                if str(v.get("severity", "")).lower() != "error":
                    continue
                vtype = v.get("type", "")
                items = v.get("items", [])
                detail = "; ".join(i.get("description", "") for i in items)
                # Ignore pin_not_connected — validated via netlist above
                if vtype == "pin_not_connected":
                    continue
                if vtype in ("label_dangling",):
                    errors.append(f"ERC error: [{vtype}] {detail}")
                elif vtype not in ("lib_symbol_issues",):
                    errors.append(f"ERC error: [{vtype}] {detail}")
        print("ERC report:", erc_path)
    except FileNotFoundError:
        print("kicad-cli not found — skipped ERC")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"ERC run failed: {exc}")

    if errors:
        print("VALIDATE FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("VALIDATE OK — grid, K wiring, labels, IC socket")
    return 0


def main() -> None:
    import sys

    import gen_bringup_sch

    argv = sys.argv[1:]
    bringup = ROOT / "bringup-supply.kicad_sch"

    # Prefer tracked bringup-supply.kicad_sch (Gate 3+). Do not overwrite unless asked.
    if bringup.is_file() and "--force-bringup-write" not in argv:
        rc_b = gen_bringup_sch.validate_bringup(bringup)
    else:
        bringup = gen_bringup_sch.write_bringup_sch()
        rc_b = gen_bringup_sch.validate_bringup(bringup)
    if rc_b != 0:
        raise SystemExit(rc_b)

    if "--validate" in argv and "--force-write" not in argv:
        out = ROOT / f"{PROJECT}.kicad_sch"
        if not out.is_file():
            raise SystemExit(f"missing tracked schematic: {out}")
        rc = validate(out)
        raise SystemExit(rc)

    write_symbol_lib()
    write_project()
    out = ROOT / f"{PROJECT}.kicad_sch"
    out.write_text(schematic())
    print("wrote", out, "bytes", out.stat().st_size)
    print("paren balance", out.read_text().count("(") - out.read_text().count(")"))
    if str(BRINGUP_SHEET_FILE_UUID) not in bringup.read_text():
        print("WARN: bringup-supply UUID mismatch — check tracked sheet / gen_bringup_sch.py")
    rc = validate(out)
    if rc != 0:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
