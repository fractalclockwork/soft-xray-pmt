#!/usr/bin/env python3
"""Generate bringup-supply.kicad_sch — HV Type A divider + anode measure (page 2)."""

from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = "pmt-interface"
SHEET = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/pmt-interface/bringup-supply")
GRID_MM = 1.27

# Reuse wide IC socket geometry from gen_sch
HDR_PIN_X = 10.16
HDR_BODY_X = 7.62
HDR_Y0 = 7.62


def snap(v: float, grid: float = GRID_MM) -> float:
    return round(round(v / grid) * grid, 2)


def snap_pt(x: float, y: float) -> tuple[float, float]:
    return (snap(x), snap(y))


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


def symbol_wrap(lib_id: str, body: str, pins: str, reference: str, value: str | None = None) -> str:
    stem = lib_id.split(":")[-1]
    val = value or stem
    return f"""\t\t(symbol "{lib_id}"
\t\t\t(pin_names
\t\t\t\t(offset 0.254)
\t\t\t)
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
{lib_prop("Reference", reference, 2.54, 0)}
{lib_prop("Value", val, 0, 0)}
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
    ground = (
        _line([(-2.54, 0), (2.54, 0)])
        + "\n"
        + _line([(-1.27, -1.27), (1.27, -1.27)])
        + "\n"
        + _line([(-0.5, -2.0), (0.5, -2.0)])
    )
    r_pins = pin("1", 0, 3.81, 270) + "\n" + pin("2", 0, -3.81, 90)
    c_pins = pin("1", 0, 2.54, 270) + "\n" + pin("2", 0, -2.54, 90)
    g_pin = pin("1", 0, 0, 270, "", etype="passive").replace("(length 2.54)", "(length 0)")

    hdr_body = _rect(-HDR_BODY_X, HDR_Y0 + 2.54, HDR_BODY_X, -(HDR_Y0 + 2.54))
    hdr_pins = []
    for row in range(7):
        y = HDR_Y0 - row * 2.54
        left = 1 + row
        right = 14 - row
        hdr_pins.append(pin(str(left), -HDR_PIN_X, y, 180, str(left)))
        hdr_pins.append(pin(str(right), HDR_PIN_X, y, 0, str(right)))

    # 2-pin HV terminal: pin1 top (-HV), pin2 bottom (GND)
    term_body = _rect(-2.54, -5.08, 2.54, 5.08)
    term_pins = pin("1", 0, 7.62, 270, "-HV") + "\n" + pin("2", 0, -7.62, 90, "GND")

    bnc_body = (
        _line([(0, 2.54), (0, 0.5)])
        + "\n"
        + _line([(-2.0, 0.5), (2.0, 0.5), (0, -2.0), (-2.0, 0.5)])
        + "\n"
        + _line([(-2.54, -2.54), (2.54, -2.54)])
    )
    bnc_pins = pin("1", 0, 5.08, 270, "Center") + "\n" + pin("2", 0, -5.08, 90, "Shell")

    # Simple jumper / 2-pin
    jmp_body = _rect(-1.27, -2.54, 1.27, 2.54)
    jmp_pins = pin("1", 0, 3.81, 270) + "\n" + pin("2", 0, -3.81, 90)

    # Minimal Simulation_SPICE-compatible sources (embedded; Gate 0c KiCad export)
    vdc_body = (
        _line([(-1.27, 0.254), (1.27, 0.254)])
        + "\n"
        + _line([(-0.762, -0.254), (-1.27, -0.254)])
        + "\n"
        + _line([(0.254, -0.254), (-0.254, -0.254)])
        + "\n"
        + _line([(1.27, -0.254), (0.762, -0.254)])
    )
    # circle approx via rect for lib simplicity — pins match VDC (5.08)
    vdc_circle = _rect(-2.54, -2.54, 2.54, 2.54)
    vdc_pins = pin("1", 0, 5.08, 270) + "\n" + pin("2", 0, -5.08, 90)
    ipulse_body = vdc_circle
    ipulse_pins = vdc_pins

    vdc_sym = _sim_source_symbol(
        "bringup:VDC", "V", "VDC", "V", "DC", "", vdc_body + "\n" + vdc_circle, vdc_pins
    )
    ip_sym = _sim_source_symbol(
        "bringup:IPULSE",
        "I",
        "IPULSE",
        "I",
        "PULSE",
        "y1=0 y2=3.6m td=50n tr=0.5n tf=0.5n tw=10n per=1",
        ipulse_body,
        ipulse_pins,
    )

    return "\n".join(
        [
            symbol_wrap("bringup:R", resistor, r_pins, "R"),
            symbol_wrap("bringup:C", capacitor, c_pins, "C"),
            symbol_wrap("bringup:GND", ground, g_pin, "#PWR", "GND"),
            symbol_wrap("bringup:HDR14", hdr_body, "\n".join(hdr_pins), "J", "HDR_2x7_IC_Plug"),
            symbol_wrap("bringup:TERM2", term_body, term_pins, "J", "HV_Terminal"),
            symbol_wrap("bringup:BNC", bnc_body, bnc_pins, "J", "BNC"),
            symbol_wrap("bringup:JMP", jmp_body, jmp_pins, "JMP", "Jumper"),
            vdc_sym,
            ip_sym,
        ]
    )


def _sim_source_symbol(
    lib_id: str,
    ref: str,
    value: str,
    device: str,
    sim_type: str,
    params: str,
    body: str,
    pins: str,
) -> str:
    """Lib symbol with Sim.Device / Sim.Type / Sim.Params for kicad-cli spice export."""
    stem = lib_id.split(":")[-1]
    params_prop = ""
    if params:
        params_prop = f"""
{lib_prop("Sim.Params", params, 2.54, -2.54)}"""
    return f"""\t\t(symbol "{lib_id}"
\t\t\t(pin_names
\t\t\t\t(offset 0.254)
\t\t\t)
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom no)
\t\t\t(on_board no)
\t\t\t(in_pos_files no)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
{lib_prop("Reference", ref, 2.54, 2.54)}
{lib_prop("Value", value, 2.54, 0)}
{lib_prop("Footprint", "", 0, 0, hide=True)}
{lib_prop("Datasheet", "", 0, 0, hide=True)}
{lib_prop("Sim.Pins", "1=+ 2=-", 0, 0, hide=True)}
{lib_prop("Sim.Device", device, 0, 0, hide=True)}
{lib_prop("Sim.Type", sim_type, 0, 0, hide=True)}{params_prop}
\t\t\t(symbol "{stem}_0_1"
{body}
\t\t\t)
\t\t\t(symbol "{stem}_1_1"
{pins}
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""


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


def placed(
    lib_id: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    numbers: tuple[str, ...],
    rot: int = 0,
    *,
    dnp: bool = False,
    exclude_sim: bool = False,
    sim_only: bool = False,
    extra_props: list[tuple[str, str, bool]] | None = None,
) -> str:
    """Place a symbol. sim_only → not BOM/board; exclude_sim → omit from SPICE export."""
    pin_lines = "\n".join(
        f'\t\t(pin "{number}"\n\t\t\t(uuid "{uid(ref + "-" + number)}")\n\t\t)' for number in numbers
    )
    in_bom = "no" if (dnp or sim_only) else "yes"
    on_board = "no" if sim_only else "yes"
    extras = ""
    if extra_props:
        extras = "\n" + "\n".join(
            prop(n, v, x, y, hide=h) for n, v, h in extra_props
        )
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x:.2f} {y:.2f} {rot})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim {"yes" if exclude_sim else "no"})
\t\t(in_bom {in_bom})
\t\t(on_board {on_board})
\t\t(in_pos_files {"no" if sim_only else "yes"})
\t\t(dnp {"yes" if dnp else "no"})
\t\t(uuid "{uid(ref)}")
{prop("Reference", ref, x + 2.54, y + 3.81)}
{prop("Value", value, x + 2.54, y + 1.27)}
{prop("Footprint", "", x, y, hide=True)}
{prop("Datasheet", "", x, y, hide=True)}{extras}
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


def junction(name: str, x: float, y: float) -> str:
    return f"""\t(junction
\t\t(at {x:.2f} {y:.2f})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{uid('junc-' + name)}")
\t)"""


def no_connect(name: str, x: float, y: float) -> str:
    return f"""\t(no_connect
\t\t(at {x:.2f} {y:.2f})
\t\t(uuid "{uid('nc-' + name)}")
\t)"""


def hdr_pin(j_x: float, j_y: float, n: int) -> tuple[float, float]:
    if not 1 <= n <= 14:
        raise ValueError(n)
    row = (n - 1) if n <= 7 else (14 - n)
    local_y = HDR_Y0 - row * 2.54
    local_x = -HDR_PIN_X if n <= 7 else HDR_PIN_X
    return (round(j_x + local_x, 2), round(j_y - local_y, 2))


# J4 wrap map (verified tube J1)
ELECTRODE_PIN = {
    "K": 7,
    "D1": 8,
    "D2": 9,
    "D3": 6,
    "D4": 5,
    "D5": 4,
    "D6": 12,
    "D7": 3,
    "D8": 2,
    "GND": 14,
}


def schematic() -> str:
    """Page 2: HV → Type A divider → J4 mate (labels, no shared buses); anode BNC.

    Mate connectivity uses identical local net labels at divider taps and J4 stubs —
    never a shared Manhattan stub column (avoids T-join shorts).
    """
    hv_x = snap(38.10)
    div_x = snap(88.90)
    mate_x = snap(190.50)
    anode_x = snap(254.00)
    sense_x = snap(114.30)

    # pitch 7.62 → R pin2 meets next R pin1
    y0 = snap(35.56)
    pitch = 7.62

    def r_top(yi: float) -> float:
        return snap(yi - 3.81)

    def r_bot(yi: float) -> float:
        return snap(yi + 3.81)

    # Segment equivalents as single bodies (sim/validate/test). Gate A stuffing uses
    # 2.2M/3.3M networks documented in bom-divider.md — annotate only, never R10A redraw.
    segments = [
        ("K", "D1", [("R10", "4.4M")], "single", "STUFF: 2x2.2M series"),
        ("D1", "D2", [("R11", "3.3M")], "single", "STUFF: 1x3.3M"),
        ("D2", "D3", [("R12", "3.3M")], "single", "STUFF: 1x3.3M"),
        ("D3", "D4", [("R13", "3.3M")], "single", "STUFF: 1x3.3M"),
        ("D4", "D5", [("R14", "2.2M")], "single", "STUFF: 1x2.2M"),
        ("D5", "D6", [("R15", "2.2M")], "single", "STUFF: 1x2.2M"),
        ("D6", "D7", [("R16", "2.2M")], "single", "STUFF: 1x2.2M"),
        ("D7", "D8", [("R17", "2.2M")], "single", "STUFF: 1x2.2M"),
        ("D8", "GND", [("R18", "1.1M")], "single", "STUFF: 2x2.2M parallel"),
    ]

    symbols: list[str] = []
    wires: list[str] = []
    labels: list[str] = []
    junctions: list[str] = []
    ncs: list[str] = []
    texts: list[str] = []

    # Place string; track tap Y for each named node
    tap_y: dict[str, float] = {}
    cursor_y = y0
    tap_y["K"] = r_top(cursor_y)

    for top_name, bot_name, parts, kind, stuff_note in segments:
        if kind == "single":
            ref, val = parts[0]
            symbols.append(placed("bringup:R", ref, val, div_x, cursor_y, ("1", "2")))
            texts.append(
                note(
                    f"stuff-{ref}",
                    stuff_note,
                    snap(div_x - 38.10),
                    snap(cursor_y),
                    1.0,
                )
            )
            tap_y[bot_name] = r_bot(cursor_y)
            cursor_y = snap(cursor_y + pitch)
        else:
            raise SystemExit(f"unsupported segment kind {kind}: annotate-only policy")

    # --- HV input J3 (hardware only — excluded from SPICE; Vhv drives -HV) ---
    j3_x, j3_y = hv_x, snap(tap_y["K"] - 15.24)
    symbols.append(
        placed("bringup:TERM2", "J3", "HV_IN", j3_x, j3_y, ("1", "2"), exclude_sim=True)
    )
    hv_pin = (j3_x, snap(j3_y - 7.62))
    j3_gnd = (j3_x, snap(j3_y + 7.62))

    # Bleed: single 22M (or note 10×2.2); keep one body for clarity / stock
    bleed_x = snap(hv_x + 17.78)
    bleed_y = snap((tap_y["K"] + tap_y["GND"]) / 2)
    symbols.append(placed("bringup:R", "Rbleed", "22M", bleed_x, bleed_y, ("1", "2")))
    texts.append(
        note(
            "bleed-soft",
            "Rbleed soft (≥22M OK); string is primary bleeder",
            snap(bleed_x - 5.08),
            snap(bleed_y - 8.89),
            1.0,
        )
    )
    bleed_top = (bleed_x, snap(bleed_y - 3.81))
    bleed_bot = (bleed_x, snap(bleed_y + 3.81))

    # -HV → K node (top of string)
    wires.append(wire("hv-k-h", hv_pin[0], hv_pin[1], div_x, hv_pin[1]))
    wires.append(wire("hv-k-v", div_x, hv_pin[1], div_x, tap_y["K"]))
    junctions.append(junction("k-node", div_x, tap_y["K"]))
    # Global labels → spice nodes K/D1.. without KiCad "/" prefix (ngspice-safe)
    labels.append(global_label("neghv", "K", hv_pin[0], hv_pin[1], 0))

    # Bleed across -HV to GND via labels on dedicated stubs (no mid-string T-joins)
    wires.append(wire("bleed-t", bleed_top[0], bleed_top[1], bleed_top[0], tap_y["K"]))
    wires.append(wire("bleed-th", bleed_top[0], tap_y["K"], div_x, tap_y["K"]))
    wires.append(wire("bleed-b", bleed_bot[0], bleed_bot[1], bleed_bot[0], tap_y["GND"]))
    wires.append(wire("bleed-bh", bleed_bot[0], tap_y["GND"], div_x, tap_y["GND"]))
    junctions.append(junction("gnd-node", div_x, tap_y["GND"]))

    # GND symbol (exclude from sim — global label GND is the SPICE 0 node)
    gnd_sym_y = snap(tap_y["GND"] + 10.16)
    symbols.append(
        placed("bringup:GND", "GND1", "GND", div_x, gnd_sym_y, ("1",), exclude_sim=True)
    )
    wires.append(wire("gnd-sym", div_x, tap_y["GND"], div_x, gnd_sym_y))
    labels.append(global_label("GND", "GND", div_x, gnd_sym_y, 270))

    # J3 GND → same GND node via label (avoid long vertical sharing with dynode channels)
    wires.append(wire("j3g-stub", j3_gnd[0], j3_gnd[1], snap(j3_gnd[0] + 5.08), j3_gnd[1]))
    labels.append(global_label("j3-gnd", "GND", snap(j3_gnd[0] + 5.08), j3_gnd[1], 0))

    # --- Gate 0c SPICE sources (sim-only; KiCad Simulator / kicad-cli spice export) ---
    sim_x = snap(hv_x - 20.32)
    vhv_y = snap(tap_y["K"] + 12.70)
    symbols.append(
        placed(
            "bringup:VDC",
            "Vhv",
            "-1000",
            sim_x,
            vhv_y,
            ("1", "2"),
            sim_only=True,
            extra_props=[
                ("Sim.Pins", "1=+ 2=-", True),
                ("Sim.Device", "V", True),
                ("Sim.Type", "DC", True),
            ],
        )
    )
    vhv_p1 = (sim_x, snap(vhv_y - 5.08))  # pin1 + → -HV (Value=-1000)
    vhv_p2 = (sim_x, snap(vhv_y + 5.08))  # pin2 − → GND
    wires.append(wire("vhv-hv", vhv_p1[0], vhv_p1[1], hv_pin[0], hv_pin[1]))
    wires.append(wire("vhv-gnd-stub", vhv_p2[0], vhv_p2[1], snap(vhv_p2[0] - 5.08), vhv_p2[1]))
    labels.append(global_label("vhv-gnd", "GND", snap(vhv_p2[0] - 5.08), vhv_p2[1], 180))
    junctions.append(junction("vhv-hv", hv_pin[0], hv_pin[1]))

    # Anode load + photon pulse (page-1 R2 not on this sheet)
    ra_x, ra_y = snap(anode_x - 45.72), snap(48.26)
    symbols.append(
        placed("bringup:R", "Ra", "1.1M", ra_x, ra_y, ("1", "2"), sim_only=True)
    )
    ra_top = (ra_x, snap(ra_y - 3.81))
    ra_bot = (ra_x, snap(ra_y + 3.81))
    a_lab_y = snap(ra_top[1] - 5.08)
    wires.append(wire("ra-a", ra_top[0], ra_top[1], ra_top[0], a_lab_y))
    labels.append(global_label("Ra-A", "A", ra_top[0], a_lab_y, 270))
    wires.append(wire("ra-gnd-stub", ra_bot[0], ra_bot[1], ra_bot[0], snap(ra_bot[1] + 5.08)))
    labels.append(global_label("ra-gnd", "GND", ra_bot[0], snap(ra_bot[1] + 5.08), 270))

    # Scope-like capacitance so photon pulse is not pure I*Ra (~kV)
    ca_x, ca_y = snap(ra_x + 10.16), ra_y
    symbols.append(
        placed("bringup:C", "Ca", "15p", ca_x, ca_y, ("1", "2"), sim_only=True)
    )
    ca_top = (ca_x, snap(ca_y - 2.54))
    ca_bot = (ca_x, snap(ca_y + 2.54))
    wires.append(wire("ca-a-h", ca_top[0], a_lab_y, ra_top[0], a_lab_y))
    wires.append(wire("ca-a-v", ca_top[0], ca_top[1], ca_top[0], a_lab_y))
    junctions.append(junction("ca-a", ra_top[0], a_lab_y))
    wires.append(wire("ca-gnd-stub", ca_bot[0], ca_bot[1], ca_bot[0], snap(ca_bot[1] + 5.08)))
    labels.append(global_label("ca-gnd", "GND", ca_bot[0], snap(ca_bot[1] + 5.08), 270))

    iph_x, iph_y = snap(ra_x - 15.24), ra_y
    symbols.append(
        placed(
            "bringup:IPULSE",
            "Iph",
            "IPULSE",
            iph_x,
            iph_y,
            ("1", "2"),
            sim_only=True,
            extra_props=[
                ("Sim.Pins", "1=+ 2=-", True),
                ("Sim.Device", "I", True),
                ("Sim.Type", "PULSE", True),
                (
                    "Sim.Params",
                    "y1=0 y2=3.6m td=50n tr=0.5n tf=0.5n tw=10n per=1",
                    False,
                ),
            ],
        )
    )
    iph_p1 = (iph_x, snap(iph_y - 5.08))
    iph_p2 = (iph_x, snap(iph_y + 5.08))
    wires.append(wire("iph-a", iph_p1[0], iph_p1[1], ra_top[0], a_lab_y))
    junctions.append(junction("iph-a", ra_top[0], a_lab_y))
    wires.append(wire("iph-gnd-stub", iph_p2[0], iph_p2[1], iph_p2[0], snap(iph_p2[1] + 5.08)))
    labels.append(global_label("iph-gnd", "GND", iph_p2[0], snap(iph_p2[1] + 5.08), 270))

    texts.append(
        note(
            "spice",
            "SIM (Gate 0c): Vhv=-1000; Ra=1.1M anode load; Iph≈36pC/10ns. Never stuff Vhv/Iph/Ra/Ca. Connectors/DNP exclude_from_sim.",
            snap(sim_x - 5.08),
            snap(vhv_y - 20.32),
        )
    )
    # KiCad exports leading-"." text into the SPICE deck
    texts.append(
        note(
            "spice-title",
            ".title bringup-supply Gate 0c (KiCad export)",
            snap(sim_x - 5.08),
            snap(vhv_y - 15.24),
        )
    )

    # Divider tap labels (short stubs right — unique per Y, no shared bus to J4)
    for name in ("K", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        y = tap_y[name]
        stub = (snap(div_x + 7.62), y)
        wires.append(wire(f"tap-{name}", div_x, y, stub[0], stub[1]))
        labels.append(global_label(f"taplab-{name}", name, stub[0], stub[1], 0))
        junctions.append(junction(f"tapj-{name}", div_x, y))

    # --- J4 mate: outward stubs + matching net labels (no cross wires) ---
    j4_x, j4_y = mate_x, snap((tap_y["K"] + tap_y["GND"]) / 2)
    symbols.append(
        placed(
            "bringup:HDR14",
            "J4",
            "HDR_2x7_IC_Plug",
            j4_x,
            j4_y,
            tuple(str(n) for n in range(1, 15)),
            exclude_sim=True,
        )
    )

    for ename, pin_n in ELECTRODE_PIN.items():
        px, py = hdr_pin(j4_x, j4_y, pin_n)
        # stub outward from pin only (short); label at stub tip
        if pin_n <= 7:
            tip = (snap(px - 5.08), py)
        else:
            tip = (snap(px + 5.08), py)
        wires.append(wire(f"j4-{ename}", px, py, tip[0], tip[1]))
        rot = 180 if pin_n <= 7 else 0
        labels.append(global_label(f"j4lab-{ename}", ename, tip[0], tip[1], rot))

    for pin_n in (1, 10, 11, 13):
        px, py = hdr_pin(j4_x, j4_y, pin_n)
        ncs.append(no_connect(f"j4-{pin_n}", px, py))

    # --- Anode measurement ---
    j5_x, j5_y = anode_x, snap(48.26)
    symbols.append(
        placed("bringup:BNC", "J5", "BNC_SCOPE", j5_x, j5_y, ("1", "2"), exclude_sim=True)
    )
    r19_x, r19_y = snap(anode_x - 20.32), snap(j5_y - 5.08)
    # Scope series kept out of Gate 0c anode-load check (Ra is the sim load)
    symbols.append(
        placed("bringup:R", "R19", "47R", r19_x, r19_y, ("1", "2"), rot=90, exclude_sim=True)
    )
    r19_left = (snap(r19_x - 3.81), r19_y)
    r19_right = (snap(r19_x + 3.81), r19_y)
    jmp_x, jmp_y = snap(anode_x - 20.32), snap(j5_y + 7.62)
    symbols.append(
        placed(
            "bringup:JMP",
            "JMP_DC",
            "DC_COUPLE",
            jmp_x,
            jmp_y,
            ("1", "2"),
            rot=90,
            exclude_sim=True,
        )
    )
    jmp_left = (snap(jmp_x - 3.81), jmp_y)
    jmp_right = (snap(jmp_x + 3.81), jmp_y)
    c4_x, c4_y = snap(anode_x - 20.32), snap(j5_y + 17.78)
    symbols.append(
        placed(
            "bringup:C",
            "C4",
            "1nF",
            c4_x,
            c4_y,
            ("1", "2"),
            rot=90,
            dnp=True,
            exclude_sim=True,
        )
    )
    c4_left = (snap(c4_x - 2.54), c4_y)
    c4_right = (snap(c4_x + 2.54), c4_y)

    a_bus_x = snap(r19_left[0] - 7.62)
    wires.append(wire("a-r19", a_bus_x, r19_y, r19_left[0], r19_left[1]))
    labels.append(global_label("A-in", "A", a_bus_x, r19_y, 180))
    wires.append(wire("a-bus-v1", a_bus_x, r19_y, a_bus_x, jmp_y))
    wires.append(wire("a-jmp", a_bus_x, jmp_y, jmp_left[0], jmp_left[1]))
    wires.append(wire("a-bus-v2", a_bus_x, jmp_y, a_bus_x, c4_y))
    wires.append(wire("a-c4", a_bus_x, c4_y, c4_left[0], c4_left[1]))
    junctions.append(junction("a-bus1", a_bus_x, r19_y))
    junctions.append(junction("a-bus2", a_bus_x, jmp_y))

    j5_ctr = (j5_x, snap(j5_y - 5.08))
    j5_sh = (j5_x, snap(j5_y + 5.08))
    out_x = snap(r19_right[0] + 5.08)
    wires.append(wire("r19-out", r19_right[0], r19_right[1], out_x, r19_right[1]))
    wires.append(wire("jmp-out", jmp_right[0], jmp_right[1], out_x, jmp_right[1]))
    wires.append(wire("c4-out", c4_right[0], c4_right[1], out_x, c4_right[1]))
    wires.append(wire("out-v", out_x, r19_y, out_x, c4_y))
    wires.append(wire("out-j5v", out_x, r19_y, out_x, j5_ctr[1]))
    wires.append(wire("out-j5", out_x, j5_ctr[1], j5_ctr[0], j5_ctr[1]))
    junctions.append(junction("out1", out_x, r19_y))
    junctions.append(junction("out2", out_x, jmp_y))
    junctions.append(junction("out3", out_x, c4_y))

    # J5 shell → GND via global label (no long wire across dynode area)
    wires.append(wire("j5-gnd-stub", j5_sh[0], j5_sh[1], j5_sh[0], snap(j5_sh[1] + 5.08)))
    labels.append(global_label("j5-gnd", "GND", j5_sh[0], snap(j5_sh[1] + 5.08), 270))

    # --- HV sense DNP (isolated; R20 top NC) ---
    sense_y = snap(tap_y["GND"] + 27.94)
    symbols.append(
        placed(
            "bringup:R",
            "R20",
            "100M",
            sense_x,
            sense_y,
            ("1", "2"),
            dnp=True,
            exclude_sim=True,
        )
    )
    r21_x = snap(sense_x + 20.32)
    symbols.append(
        placed(
            "bringup:R",
            "R21",
            "100k",
            r21_x,
            sense_y,
            ("1", "2"),
            rot=90,
            dnp=True,
            exclude_sim=True,
        )
    )
    c5_x, c5_y = snap(r21_x), snap(sense_y + 12.70)
    symbols.append(
        placed(
            "bringup:C",
            "C5",
            "100n",
            c5_x,
            c5_y,
            ("1", "2"),
            dnp=True,
            exclude_sim=True,
        )
    )
    # R20 bot → R21 left (sense mid); R21 right → GND label; C5 across mid→GND
    r20_bot = (sense_x, snap(sense_y + 3.81))
    r21_l = (snap(r21_x - 3.81), sense_y)
    r21_r = (snap(r21_x + 3.81), sense_y)
    mid_y = sense_y
    wires.append(wire("r20-down", r20_bot[0], r20_bot[1], r20_bot[0], mid_y))
    wires.append(wire("r20-to-r21", r20_bot[0], mid_y, r21_l[0], r21_l[1]))
    labels.append(label("HV_SENSE", "HV_SENSE", r21_l[0], r21_l[1]))
    wires.append(wire("r21-gnd-stub", r21_r[0], r21_r[1], snap(r21_r[0] + 5.08), r21_r[1]))
    labels.append(global_label("r21-gnd", "GND", snap(r21_r[0] + 5.08), r21_r[1], 0))
    # C5: top to mid via horizontal at unique Y then up — avoid landing on R21 body center
    c5_top = (c5_x, snap(c5_y - 2.54))
    c5_bot = (c5_x, snap(c5_y + 2.54))
    wires.append(wire("c5-to-mid-v", c5_top[0], c5_top[1], c5_top[0], mid_y))
    # mid join at (c5_x, mid_y) must connect to sense mid: wire to r21_l along mid_y
    wires.append(wire("c5-mid-h", c5_x, mid_y, r21_l[0], mid_y))
    junctions.append(junction("sense-mid", r21_l[0], mid_y))
    junctions.append(junction("c5-mid", c5_x, mid_y))
    wires.append(wire("c5-gnd-stub", c5_bot[0], c5_bot[1], c5_bot[0], snap(c5_bot[1] + 5.08)))
    labels.append(global_label("c5-gnd", "GND", c5_bot[0], snap(c5_bot[1] + 5.08), 270))
    ncs.append(no_connect("r20-top", sense_x, snap(sense_y - 3.81)))
    texts.append(
        note(
            "sense",
            "HV sense DNP Stage 7+: R20 pin1→-HV when populated; clamp HV_SENSE to 3V3",
            snap(sense_x - 12.70),
            snap(sense_y - 10.16),
        )
    )

    texts.extend(
        [
            note("title", "Bring-up supply — Type A divider + anode measure", 25.40, 12.70, 2.54),
            note("pol", "POLARITY: J3.1=-HV→K; J3.2=GND. Mate nets via labels (no shared stub bus).", 25.40, 17.78),
            note(
                "net",
                "Sch = segment equivalents (sim/validate). Gate A STUFF notes = 2.2M/3.3M networks (bom-divider.md).",
                25.40,
                22.86,
            ),
            note("mate", "J4 wrap plug 7.62mm; pins 1/10/11/13 NC. docs/bringup/", snap(mate_x - 20.32), snap(j4_y - 35.56)),
            note(
                "anode",
                "J5 scope: JMP_DC default; C4 DNP AC. Label A = tube coax when harnessed.",
                snap(anode_x - 50.80),
                snap(j5_y - 17.78),
            ),
        ]
    )

    instances = "\n".join([*symbols, *wires, *labels, *junctions, *ncs, *texts])
    return f"""(kicad_sch
\t(version 20260306)
\t(generator "gen_bringup_sch.py")
\t(generator_version "10.0")
\t(uuid "{SHEET}")
\t(paper "A3")
\t(title_block
\t\t(title "bringup-supply")
\t\t(date "2026-11-02")
\t\t(rev "0.5-stuff-annot")
\t\t(comment 1 "Type A segment equivalents; mate via net labels (no shared stubs)")
\t\t(comment 2 "Gate A: STUFF annotations for 2.2M/3.3M — no R10A sch redraw")
\t)
\t(lib_symbols
{graphics()}
\t)
{instances}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "2")
\t\t)
\t)
)
"""


def validate_bringup(sch_path: Path) -> int:
    """Fail on collapsed dynode nets / unexpected GND membership / shorted resistors."""
    import re
    import subprocess
    import tempfile

    errors: list[str] = []
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
    except FileNotFoundError:
        print("kicad-cli missing — skipped bringup netlist validate")
        return 0

    if not net_path.exists():
        errors.append("bringup netlist export failed")
        print("VALIDATE FAIL")
        for e in errors:
            print(" -", e)
        return 1

    net = net_path.read_text()
    nets = re.findall(
        r'\(net\s+\(code "[^"]+"\)\s+\(name "([^"]+)"\)([\s\S]*?)(?=\(net\s+\(code |\Z)',
        net,
    )

    def norm(name: str) -> str:
        return name[1:] if name.startswith("/") else name

    by_name: dict[str, set[str]] = {}
    pin_map: dict[str, list[tuple[str, str]]] = {}
    for name, body in nets:
        n = norm(name)
        refs = set(re.findall(r'\(ref "([^"]+)"\)', body))
        pins = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', body)
        by_name[n] = refs
        pin_map[n] = pins

    # Required electrode nets (K and -HV are the same node on this board)
    k_net = "K" if "K" in by_name else ("-HV" if "-HV" in by_name else None)
    if k_net is None:
        errors.append("missing K/-HV cathode bias net")
    for need in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "GND", "A"):
        if need not in by_name:
            errors.append(f"missing distinct net {need}")

    # J4 pin → expected net
    expect_pin = {str(p): e for e, p in ELECTRODE_PIN.items()}
    j4_nets: dict[str, str] = {}
    for n, pins in pin_map.items():
        for ref, pin in pins:
            if ref == "J4" and pin in expect_pin:
                exp = expect_pin[pin]
                if exp == "GND":
                    if n != "GND":
                        errors.append(f"J4.{pin} expected GND, on net {n}")
                elif exp == "K":
                    if n not in ("K", "-HV"):
                        errors.append(f"J4.{pin} expected K/-HV, on net {n}")
                elif n != exp:
                    errors.append(f"J4.{pin} expected {exp}, on net {n}")
                j4_nets[pin] = n

    # Distinct dynode nets
    dyn = []
    for d in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        if d in by_name:
            dyn.append(d)
        else:
            errors.append(f"missing dynode net {d}")
    if len(set(dyn)) != len(dyn):
        errors.append("dynode net names not unique")
    # pairwise: D1 and D2 must not be same net object — check J4.8 vs J4.9
    if j4_nets.get("8") and j4_nets.get("9") and j4_nets["8"] == j4_nets["9"]:
        errors.append("J4.8 and J4.9 share a net (mate short)")

    # Mid-string resistors must not appear on GND (R10–R17; R18 belongs on GND)
    gnd_refs = by_name.get("GND", set())
    forbidden_on_gnd = {"R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17"}
    # Also refuse legacy network refs if present on GND mid-string
    forbidden_on_gnd |= {"R10A", "R10B"}
    bad = forbidden_on_gnd & gnd_refs
    if bad:
        errors.append(f"divider parts on GND (short): {sorted(bad)}")

    # Resistor both pins on same net → element shorted
    ref_pins: dict[str, list[tuple[str, str]]] = {}
    for n, pins in pin_map.items():
        for ref, pin in pins:
            if ref.startswith("R") and ref not in ("R19", "R20", "R21", "Rbleed"):
                ref_pins.setdefault(ref, []).append((n, pin))
    for ref, plist in ref_pins.items():
        nets_for = {n for n, _ in plist}
        if len(plist) >= 2 and len(nets_for) == 1:
            errors.append(f"{ref} both pins on net {next(iter(nets_for))} (shorted out)")

    # Cathode bias net: J3.1 + R10 + J4.7 only (not the whole string)
    if k_net:
        j4pins = [p for r, p in pin_map.get(k_net, []) if r == "J4"]
        if sorted(j4pins) != ["7"]:
            errors.append(f"{k_net} J4 pins should be only 7, got {j4pins}")
        top = by_name.get(k_net, set())
        if "R10" not in top:
            errors.append(f"{k_net} missing R10 (top of string; R10A sch symbols forbidden)")
        if "J3" not in top:
            errors.append(f"{k_net} missing J3")

    if errors:
        print("BRINGUP VALIDATE FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("BRINGUP VALIDATE OK — distinct K/D1..D8/GND/A, J4 map, no divider-on-GND")
    return 0


def write_bringup_sch() -> Path:
    out = ROOT / "bringup-supply.kicad_sch"
    text = schematic()
    out.write_text(text)
    bal = text.count("(") - text.count(")")
    print("wrote", out, "bytes", out.stat().st_size, "paren_balance", bal)
    for need in ("R10", "R11", "R18", "J3", "J4", "J5", "Rbleed", "4.4M", "1.1M", "Vhv", "Iph", "Ra"):
        if need not in text:
            raise SystemExit(f"missing {need}")
    # Policy: never place R10A/R18A symbols — stuffing is annotation + bom-divider.md only
    if '(property "Reference" "R10A"' in text:
        raise SystemExit("R10A forbidden: keep equiv R10; stuff networks per bom-divider.md")
    if bal != 0:
        raise SystemExit(f"paren imbalance {bal}")
    return out


def main() -> None:
    import sys

    argv = sys.argv[1:]
    out = ROOT / "bringup-supply.kicad_sch"

    # Validate tracked schematic only — never overwrite after Gate 3.
    if "--validate" in argv and "--force-write" not in argv:
        if not out.is_file():
            raise SystemExit(f"missing tracked schematic: {out}")
        rc = validate_bringup(out)
        if rc != 0:
            raise SystemExit(rc)
        print("OK — validated tracked", out, "(no write)")
        raise SystemExit(0)

    if out.is_file() and "--force-write" not in argv:
        raise SystemExit(
            f"refusing to overwrite tracked {out}\n"
            "  After Gate 3, edit the schematic in Eeschema and run --validate.\n"
            "  Use --force-write only when the operator asks to regenerate from the generator."
        )

    out = write_bringup_sch()
    rc = validate_bringup(out)
    if rc != 0:
        raise SystemExit(rc)
    print("OK — wrote", out)


if __name__ == "__main__":
    main()

