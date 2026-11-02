#!/usr/bin/env python3
"""Generate photo-matched 2-layer filter PCB for the XP3312 stock I/O board.

Layout follows docs/pin-reconciliation.md + docs/photo-trace-map.md:
  - circular outline around the flying-lead pin circle
  - central wrap-numbered DIP-14–class J1 (7.62 mm rows)
  - B.Cu H/V/45 dynode fan-out (header/plastic side)
  - F.Cu filter in DIP channel; C1/R1 at K; R2 at A
  - coax on header side; J1.1 / 10 / 11 unrouted NC
"""

from __future__ import annotations

import math
import re
import uuid
from pathlib import Path

from tube_geo import FP_PIN_CIRCLE_DIA_MM, pin_positions

ROOT = Path(__file__).resolve().parent
PRETTY = ROOT / "libraries" / "XP3312.pretty"
KICAD_FP = Path("/usr/share/kicad/footprints")
PROJECT = "pmt-interface"
SHEET = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/pmt-interface-pcb")

BOARD_R_MM = 22.0  # pin circle 31.8 mm + thin rim (photos: pads near edge)
CX, CY = 100.0, 100.0
PIN_R = FP_PIN_CIRCLE_DIA_MM / 2.0

W_DYNODE = 0.30
W_FILTER = 0.25
W_GND = 0.40
W_ANODE = 0.30


# Wide IC / DIP-14 socket: 7.62 mm (300 mil) row spacing, wrap numbering.
# NOT 2.54 mm dual-row ribbon header geometry.
J1_ROW_X = 3.81  # half of 7.62


def j1_local(n: int) -> tuple[float, float]:
    if not 1 <= n <= 14:
        raise ValueError(n)
    if n <= 7:
        return (-J1_ROW_X, 7.62 - (n - 1) * 2.54)
    return (J1_ROW_X, 7.62 - (14 - n) * 2.54)


def uid(name: str) -> str:
    return str(uuid.uuid5(SHEET, name))


def rot_pt(lx: float, ly: float, ang_deg: float) -> tuple[float, float]:
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)
    return (lx * c - ly * s, lx * s + ly * c)


def fp_world(lx: float, ly: float, fx: float, fy: float, rot_deg: float) -> tuple[float, float]:
    """Footprint-local → board XY. KiCad R maps as math rotation -R (Y-down)."""
    dx, dy = rot_pt(lx, ly, -rot_deg)
    return (fx + dx, fy + dy)


def load_mod(path: Path) -> str:
    return path.read_text().strip()


def indent_body(mod_text: str, spaces: int = 2) -> str:
    lines = mod_text.strip().splitlines()
    pad = " " * spaces
    return "\n".join(pad + ln if ln else ln for ln in lines[1:-1])


def inject_pad_nets(mod_text: str, pad_nets: dict[str, tuple[int, str]], ref: str) -> str:
    def repl(m: re.Match[str]) -> str:
        pad_num = m.group(1)
        block = m.group(0)
        if "(net " in block:
            return block
        uniq = uid(f"{ref}-pad-{pad_num}-{m.start()}")
        if pad_num not in pad_nets:
            insert = f'\n\t\t(uuid "{uniq}")'
        else:
            net_i, net_name = pad_nets[pad_num]
            insert = f'\n\t\t(net {net_i} "{net_name}")\n\t\t(uuid "{uniq}")'
        block = block.rstrip()
        return block[:-1] + insert + "\n\t)"

    return re.sub(r'\(pad "([^"]+)"[\s\S]*?\n\t\)', repl, mod_text)


def hide_fp_silk_text(mod_text: str) -> str:
    """Hide Reference/Value silk to cut silk_over_copper noise on a dense board."""

    def hide_prop(m: re.Match[str]) -> str:
        block = m.group(0)
        if "(hide yes)" in block:
            return block
        return block[:-1] + "\n\t\t(hide yes)\n\t)"

    return re.sub(
        r'\(property "(?:Reference|Value)"[\s\S]*?\n\t\)',
        hide_prop,
        mod_text,
    )


def place_footprint(
    lib_id: str,
    mod_text: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rot: float,
    pad_nets: dict[str, tuple[int, str]],
    layer: str = "F.Cu",
) -> str:
    mod = inject_pad_nets(mod_text, pad_nets, ref)
    mod = hide_fp_silk_text(mod)
    mod = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', mod, count=1)
    mod = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{value}"', mod, count=1)
    body = indent_body(mod, 2)
    return f"""\t(footprint "{lib_id}"
\t\t(layer "{layer}")
\t\t(uuid "{uid("fp-" + ref)}")
\t\t(at {x:.4f} {y:.4f} {rot:.4f})
{body}
\t)"""


def segment(
    name: str, x1: float, y1: float, x2: float, y2: float, width: float, layer: str, net_id: int
) -> str:
    return f"""\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width:.3f})
\t\t(layer "{layer}")
\t\t(net {net_id})
\t\t(uuid "{uid("seg-" + name)}")
\t)"""


def via(name: str, x: float, y: float, net_id: int, size: float = 0.8, drill: float = 0.4) -> str:
    return f"""\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size {size})
\t\t(drill {drill})
\t\t(layers "F.Cu" "B.Cu")
\t\t(net {net_id})
\t\t(uuid "{uid("via-" + name)}")
\t)"""


def path_pts(
    name: str, pts: list[tuple[float, float]], width: float, layer: str, net_id: int
) -> list[str]:
    out: list[str] = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9:
            continue
        out.append(segment(f"{name}-{i}", a[0], a[1], b[0], b[1], width, layer, net_id))
    return out


def ang_of(p: tuple[float, float]) -> float:
    return math.atan2(p[1] - CY, p[0] - CX)


def polar_pt(r: float, ang: float) -> tuple[float, float]:
    return (CX + r * math.cos(ang), CY + r * math.sin(ang))


def arc_pts(r: float, a0: float, a1: float, step_deg: float = 12.0) -> list[tuple[float, float]]:
    """Shortest arc from a0→a1 at radius r (inclusive of endpoints)."""
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    n = max(1, int(abs(math.degrees(da)) / step_deg))
    return [polar_pt(r, a0 + da * i / n) for i in range(n + 1)]


def hv45(a: tuple[float, float], b: tuple[float, float]) -> list[tuple[float, float]]:
    """Photo lands: horizontal / vertical / 45° only (IMG_7002 / 7015 / 7020)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if abs(dx) < 0.05 or abs(dy) < 0.05:
        return [a, b]
    adx, ady = abs(dx), abs(dy)
    if abs(adx - ady) < 0.05:
        return [a, b]  # already a pure 45°
    # 45° then ortho finish
    s = min(adx, ady)
    mid = (ax + math.copysign(s, dx), ay + math.copysign(s, dy))
    if abs(mid[0] - bx) < 0.05 and abs(mid[1] - by) < 0.05:
        return [a, b]
    return [a, mid, b]


def join_hv(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Chain points with hv45 between each pair; drop duplicate joints."""
    if len(pts) < 2:
        return pts
    out: list[tuple[float, float]] = [pts[0]]
    for i in range(len(pts) - 1):
        seg = hv45(pts[i], pts[i + 1])
        out.extend(seg[1:])
    return out


def build_pcb() -> str:
    pins = pin_positions(PIN_R)
    by_name = {p.name: p for p in pins if p.name != "ic"}

    net_names = [
        "",
        "GND",
        "K",
        "A",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "J1.13",
        "BYPASS_MID",
        "R1_J1",
    ]
    nid = {n: i for i, n in enumerate(net_names)}

    k = by_name["K"]
    lx7, ly7 = j1_local(7)
    ang_local = math.degrees(math.atan2(ly7, lx7))
    ang_k = math.degrees(math.atan2(k.y, k.x))
    j1_rot = ang_local - ang_k

    def j1_pad(n: int) -> tuple[float, float]:
        return fp_world(*j1_local(n), CX, CY, j1_rot)

    def tube_pad(name: str) -> tuple[float, float]:
        p = by_name[name]
        return (CX + p.x, CY + p.y)

    def polar(r: float, ang: float) -> tuple[float, float]:
        return (CX + r * math.cos(ang), CY + r * math.sin(ang))

    def smd_pads(x: float, y: float, rot: float, half: float = 0.9125):
        return fp_world(-half, 0, x, y, rot), fp_world(half, 0, x, y, rot)

    def disc_pads(x: float, y: float, rot: float):
        return fp_world(0, 0, x, y, rot), fp_world(5.0, 0, x, y, rot)

    def orient(x, y, rot, want_p1_near, half=0.9125):
        p1, p2 = smd_pads(x, y, rot, half)
        if math.hypot(p1[0] - want_p1_near[0], p1[1] - want_p1_near[1]) > math.hypot(
            p2[0] - want_p1_near[0], p2[1] - want_p1_near[1]
        ):
            rot = (rot + 180.0) % 360.0
            p1, p2 = smd_pads(x, y, rot, half)
        return rot, p1, p2

    a_pos, k_pos = tube_pad("A"), tube_pad("K")
    a_ang = math.atan2(by_name["A"].y, by_name["A"].x)
    k_ang = math.atan2(k.y, k.x)

    def j1_xy(lx: float, ly: float) -> tuple[float, float]:
        """Point in J1 footprint local coords → board."""
        return fp_world(lx, ly, CX, CY, j1_rot)

    j7, j2p, j13, j14 = j1_pad(7), j1_pad(2), j1_pad(13), j1_pad(14)

    # --- Photo-locked placement (IMG_7005 / 7002 / 7020) ---
    # F.Cu = SMD/component side: filter sits IN THE CHANNEL between DIP rows.
    # B.Cu = header/pin side: ortho/45° fan-out (coax to the A/K side of board).
    #
    # Local J1: pins 2 & 13 share Y≈+5.08 (same end as 1/14). Channel = local X≈0.

    # Filter trio in DIP channel (IMG_7005): C3(D8) | R3(100) | C2(J1.13)
    # Pad axis along local Y so 0805 bodies fit between the 7.62 mm rows.
    y_axis = fp_world(0, 1, 0, 0, j1_rot)
    smd_rot = math.degrees(math.atan2(y_axis[1], y_axis[0]))
    c3_xy = j1_xy(-1.7, 3.2)
    r3_xy = j1_xy(0.0, 1.4)
    c2_xy = j1_xy(1.7, 3.2)
    mid = j1_xy(0.0, 2.4)
    c3_rot = c2_rot = r3_rot = smd_rot

    # Cathode: blue disc outside socket toward K; R1 between K and J1.7
    c1_x, c1_y = polar(14.0, k_ang + math.radians(8))
    c1_rot = math.degrees(k_ang) + 90.0
    r1_x = 0.45 * k_pos[0] + 0.55 * j7[0]
    r1_y = 0.45 * k_pos[1] + 0.55 * j7[1]
    r1_rot = math.degrees(math.atan2(j7[1] - k_pos[1], j7[0] - k_pos[0]))

    # Coax on rim by A (IMG_7002); R2 nearby on F.Cu
    j2_xy = polar(18.2, a_ang - math.radians(5))
    j2_rot = math.degrees(a_ang) + 90.0
    # Keep R2 on the A/K side of the coax, clear of the D8 tube pad
    r2_xy = polar(12.2, a_ang - math.radians(12))
    r2_rot = smd_rot

    r1_rot, r1_p1, r1_p2 = orient(r1_x, r1_y, r1_rot, k_pos)
    c1_p1, c1_p2 = disc_pads(c1_x, c1_y, c1_rot)
    if math.hypot(c1_p1[0] - k_pos[0], c1_p1[1] - k_pos[1]) > math.hypot(
        c1_p2[0] - k_pos[0], c1_p2[1] - k_pos[1]
    ):
        c1_rot = (c1_rot + 180.0) % 360.0
        c1_p1, c1_p2 = disc_pads(c1_x, c1_y, c1_rot)

    # Filter pads: pin-side pad toward its J1 pin; inner pad toward mid/R3
    c3_rot, c3_p1, c3_p2 = orient(c3_xy[0], c3_xy[1], c3_rot, j2p)
    if math.hypot(c3_p2[0] - mid[0], c3_p2[1] - mid[1]) > math.hypot(
        c3_p1[0] - mid[0], c3_p1[1] - mid[1]
    ):
        # keep p1 near j2p (already), ensure p2 is the mid side by flipping only if needed
        pass
    if math.hypot(c3_p1[0] - j2p[0], c3_p1[1] - j2p[1]) > math.hypot(
        c3_p2[0] - j2p[0], c3_p2[1] - j2p[1]
    ):
        c3_rot = (c3_rot + 180.0) % 360.0
        c3_p1, c3_p2 = smd_pads(c3_xy[0], c3_xy[1], c3_rot)

    c2_rot, c2_p1, c2_p2 = orient(c2_xy[0], c2_xy[1], c2_rot, j13)
    if math.hypot(c2_p1[0] - j13[0], c2_p1[1] - j13[1]) > math.hypot(
        c2_p2[0] - j13[0], c2_p2[1] - j13[1]
    ):
        c2_rot = (c2_rot + 180.0) % 360.0
        c2_p1, c2_p2 = smd_pads(c2_xy[0], c2_xy[1], c2_rot)

    # R3: pad1 BYPASS_MID (toward mid), pad2 GND (toward J1.14)
    r3_rot, r3_p1, r3_p2 = orient(r3_xy[0], r3_xy[1], r3_rot, mid)

    r2_rot, r2_p1, r2_p2 = orient(r2_xy[0], r2_xy[1], r2_rot, a_pos)

    tube_mod = load_mod(PRETTY / "XP3312_FlyingLead.kicad_mod")
    hdr_mod = load_mod(PRETTY / "HDR_2x7_IC_Socket.kicad_mod")
    smb_mod = load_mod(PRETTY / "COAX_Edge.kicad_mod")
    disc_mod = load_mod(KICAD_FP / "Capacitor_THT.pretty" / "C_Disc_D7.5mm_W2.5mm_P5.00mm.kicad_mod")
    r0805 = load_mod(KICAD_FP / "Resistor_SMD.pretty" / "R_0805_2012Metric.kicad_mod")
    c0805 = load_mod(KICAD_FP / "Capacitor_SMD.pretty" / "C_0805_2012Metric.kicad_mod")

    electrode_net = {
        "1": "D1",
        "3": "D2",
        "4": "D3",
        "7": "D4",
        "8": "D5",
        "9": "D6",
        "10": "D7",
        "11": "D8",
        "12": "A",
        "16": "K",
    }
    tube_nets = {num: (nid[n], n) for num, n in electrode_net.items()}
    j1_map = {
        "2": "D8",
        "3": "D7",
        "4": "D5",
        "5": "D4",
        "6": "D3",
        "7": "R1_J1",
        "8": "D1",
        "9": "D2",
        "12": "D6",
        "13": "J1.13",
        "14": "GND",
    }
    j1_nets = {p: (nid[n], n) for p, n in j1_map.items()}

    footprints = [
        place_footprint("XP3312:XP3312_FlyingLead", tube_mod, "U1", "XP3312/SQ", CX, CY, 0.0, tube_nets),
        place_footprint(
            "XP3312:HDR_2x7_IC_Socket", hdr_mod, "J1", "HDR_2x7_IC_Socket", CX, CY, j1_rot, j1_nets
        ),
        place_footprint(
            "XP3312:COAX_Edge",
            smb_mod,
            "J2",
            "COAX",
            j2_xy[0],
            j2_xy[1],
            j2_rot,
            {"1": (nid["A"], "A"), "2": (nid["GND"], "GND")},
            layer="B.Cu",
        ),
        place_footprint(
            "Capacitor_THT:C_Disc_D7.5mm_W2.5mm_P5.00mm",
            disc_mod,
            "C1",
            "4.7nF 2kV",
            c1_x,
            c1_y,
            c1_rot,
            {"1": (nid["K"], "K"), "2": (nid["GND"], "GND")},
        ),
        place_footprint(
            "Resistor_SMD:R_0805_2012Metric",
            r0805,
            "R1",
            "1k",
            r1_x,
            r1_y,
            r1_rot,
            {"1": (nid["K"], "K"), "2": (nid["R1_J1"], "R1_J1")},
        ),
        place_footprint(
            "Resistor_SMD:R_0805_2012Metric",
            r0805,
            "R2",
            "1.1M",
            r2_xy[0],
            r2_xy[1],
            r2_rot,
            {"1": (nid["A"], "A"), "2": (nid["GND"], "GND")},
        ),
        place_footprint(
            "Resistor_SMD:R_0805_2012Metric",
            r0805,
            "R3",
            "10R",
            r3_xy[0],
            r3_xy[1],
            r3_rot,
            {"1": (nid["BYPASS_MID"], "BYPASS_MID"), "2": (nid["GND"], "GND")},
        ),
        place_footprint(
            "Capacitor_SMD:C_0805_2012Metric",
            c0805,
            "C3",
            "MLCC D8",
            c3_xy[0],
            c3_xy[1],
            c3_rot,
            {"1": (nid["D8"], "D8"), "2": (nid["BYPASS_MID"], "BYPASS_MID")},
        ),
        place_footprint(
            "Capacitor_SMD:C_0805_2012Metric",
            c0805,
            "C2",
            "MLCC J1.13",
            c2_xy[0],
            c2_xy[1],
            c2_rot,
            {"1": (nid["J1.13"], "J1.13"), "2": (nid["BYPASS_MID"], "BYPASS_MID")},
        ),
    ]

    segs: list[str] = []
    vias: list[str] = []

    def route(name: str, pts: list[tuple[float, float]], w: float, layer: str, net: int) -> None:
        nonlocal segs
        segs += path_pts(name, pts, w, layer, net)

    def route_hv(name: str, a, b, w: float, layer: str, net: int) -> None:
        route(name, hv45(a, b), w, layer, net)

    def j1_escape(hp: int, out: float = 2.8) -> tuple[float, float]:
        lx, ly = j1_local(hp)
        return j1_xy(math.copysign(abs(lx) + out, lx), ly)

    def rim_to_gate(a: tuple[float, float], gate: tuple[float, float], r: float = 20.6) -> list[tuple[float, float]]:
        """Walk the outer rim to a gate outside the DIP, then H/V/45 into the gate."""
        a0, a1 = ang_of(a), ang_of(gate)
        return [a, polar(r, a0), *arc_pts(r, a0, a1, step_deg=12.0)[1:], polar(r, a1), gate]

    # Gate just outside J1.14 (right row, pin-1/14 end) — final stub into pad
    gnd_gate = j1_xy(J1_ROW_X + 3.2, 8.0)

    # B.Cu photo lands: H/V/45 tube → side-escape → pin (D8 on F.Cu with its filter)
    for ename, hp in [
        ("D7", 3),
        ("D5", 4),
        ("D4", 5),
        ("D3", 6),
        ("D1", 8),
        ("D2", 9),
        ("D6", 12),
    ]:
        esc, hdr = j1_escape(hp, out=3.4 if hp == 4 else 2.8), j1_pad(hp)
        route(f"{ename}-rad", join_hv([tube_pad(ename), esc, hdr]), W_DYNODE, "B.Cu", nid[ename])
    route("D8-rad", join_hv([tube_pad("D8"), j1_escape(2), j1_pad(2)]), W_DYNODE, "F.Cu", nid["D8"])

    # F.Cu cathode cluster (SMD side — IMG_7005 / 6989)
    route_hv("K-r1", k_pos, r1_p1, W_DYNODE, "F.Cu", nid["K"])
    route_hv("K-c1", k_pos, c1_p1, W_DYNODE, "F.Cu", nid["K"])
    route_hv("r1-j7", r1_p2, j7, W_DYNODE, "F.Cu", nid["R1_J1"])

    # GND: R3 down the channel center; C1/coax via rim → gate → J1.14
    route_hv("r3-gnd", r3_p2, j1_xy(0.0, 6.0), W_GND, "F.Cu", nid["GND"])
    route_hv("r3-gnd2", j1_xy(0.0, 6.0), j14, W_GND, "F.Cu", nid["GND"])
    route("c1-gnd", rim_to_gate(c1_p2, gnd_gate), W_GND, "F.Cu", nid["GND"])
    route_hv("gnd-j14", gnd_gate, j14, W_GND, "F.Cu", nid["GND"])
    sh = fp_world(0, -2.54, j2_xy[0], j2_xy[1], j2_rot)
    route_hv("r2-gnd", r2_p2, sh, W_GND, "F.Cu", nid["GND"])
    route("j2-gnd", rim_to_gate(sh, gnd_gate), W_GND, "F.Cu", nid["GND"])

    # F.Cu filter stubs in DIP channel
    route_hv("d8-c3", j2p, c3_p1, W_FILTER, "F.Cu", nid["D8"])
    route_hv("c3-mid", c3_p2, mid, W_FILTER, "F.Cu", nid["BYPASS_MID"])
    route_hv("j13-c2", j13, c2_p1, W_FILTER, "F.Cu", nid["J1.13"])
    route_hv("c2-mid", c2_p2, mid, W_FILTER, "F.Cu", nid["BYPASS_MID"])
    route_hv("mid-r3", mid, r3_p1, W_FILTER, "F.Cu", nid["BYPASS_MID"])

    # Anode: R2 on F.Cu; coax on B.Cu
    route_hv("a-r2", a_pos, r2_p1, W_ANODE, "F.Cu", nid["A"])
    route_hv("a-j2", a_pos, j2_xy, W_ANODE, "B.Cu", nid["A"])

    nets_sexpr = "\n".join(f'\t(net {i} "{n}")' for i, n in enumerate(net_names))
    edge = f"""\t(gr_circle
\t\t(center {CX:.4f} {CY:.4f})
\t\t(end {CX + BOARD_R_MM:.4f} {CY:.4f})
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "Edge.Cuts")
\t\t(uuid "{uid("edge")}")
\t)"""
    notes = f"""\t(gr_text "XP3312 filter PCB clone (2-layer)\\nJ1 = DIP-14 wide IC socket (7.62mm rows, wrap 1-7|14-8)\\nH/V/45 fan-out B.Cu; filter in DIP channel F.Cu; J1.1/10/11 NC\\nNot IDC ribbon Odd/Even header"
\t\t(at 78 70 0)
\t\t(layer "Cmts.User")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.2 1.2)
\t\t\t\t(thickness 0.18)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid("note")}")
\t)"""

    return f"""(kicad_pcb
\t(version 20241229)
\t(generator "gen_pcb.py")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "pmt-interface filter board")
\t\t(date "2026-11-01")
\t\t(rev "0.2")
\t\t(comment 1 "Photo-matched 2-layer clone of stock XP3312 I/O filter PCB")
\t\t(comment 2 "Nets from continuity 2026-11-01; J1.1/10/11 unrouted NC")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive")
\t\t(33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user)
\t\t(35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user)
\t\t(39 "F.Mask" user)
\t\t(40 "Dwgs.User" user "User.Drawings")
\t\t(41 "Cmts.User" user "User.Comments")
\t\t(42 "Eco1.User" user "User.Eco1")
\t\t(43 "Eco2.User" user "User.Eco2")
\t\t(44 "Edge.Cuts" user)
\t\t(45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard")
\t\t(47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user "B.Fabrication")
\t\t(49 "F.Fab" user "F.Fabrication")
\t)
\t(setup
\t\t(pad_to_mask_clearance 0.0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t)
{nets_sexpr}
{notes}
{edge}
{chr(10).join(footprints)}
{chr(10).join(segs)}
{chr(10).join(vias)}
)
"""


def update_fp_lib_table() -> None:
    (ROOT / "fp-lib-table").write_text(
        """(fp_lib_table
  (version 7)
  (lib (name "XP3312")(type "KiCad")(uri "${KIPRJMOD}/libraries/XP3312.pretty")(options "")(descr "XP3312 tube + wrap header footprints"))
)
"""
    )


def main() -> None:
    update_fp_lib_table()
    out = ROOT / f"{PROJECT}.kicad_pcb"
    out.write_text(build_pcb())
    print("wrote", out)
    print("board OD", 2 * BOARD_R_MM, "mm; center", CX, CY)


if __name__ == "__main__":
    main()
