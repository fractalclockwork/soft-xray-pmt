#!/usr/bin/env python3
"""bringup-supply.kicad_pcb — Type A HV divider + anode card.

Tracked PCB is source of truth after Gate 5 (skill kicad-gated-sch-pcb; docs/bringup/design-process.md).

  --force-place  wipe/create placement draft (operator must re-do Gate 5)
  --snap         snap XY to 2.54 mm / rot to 90°; keep operator layout; clear copper
  --route        Manhattan route from footprint positions in the tracked file
  (default)      refuse if file exists

Layer policy: F.Cu=K, B.Cu=GND, InN=dynode/A/SCOPE. Then kicad-cli pcb drc (Gate 9).
"""

from __future__ import annotations

import math
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRETTY = ROOT / "libraries" / "XP3312.pretty"
KICAD_FP = Path("/usr/share/kicad/footprints")
SHEET = uuid.uuid5(uuid.NAMESPACE_URL, "kicad/bringup-supply-pcb")
G = 2.54
HIT = 2.0  # mm — THT pad keep-out (pads short all copper layers; J4 pitch 2.54)
OUT = ROOT / "bringup-supply.kicad_pcb"

X0, Y0 = 20.0, 20.0
W, H = 130.0, 160.0

NET_NAMES = [
    "",
    "GND",
    "K",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7",
    "D8",
    "A",
    "SCOPE",
]
NID = {n: i for i, n in enumerate(NET_NAMES)}

J4_NET = {
    "2": "D8",
    "3": "D7",
    "4": "D5",
    "5": "D4",
    "6": "D3",
    "7": "K",
    "8": "D1",
    "9": "D2",
    "12": "D6",
    "14": "GND",
}

DIVIDER = [
    ("R10", "4.4M", "K", "D1"),
    ("R11", "3.3M", "D1", "D2"),
    ("R12", "3.3M", "D2", "D3"),
    ("R13", "3.3M", "D3", "D4"),
    ("R14", "2.2M", "D4", "D5"),
    ("R15", "2.2M", "D5", "D6"),
    ("R16", "2.2M", "D6", "D7"),
    ("R17", "2.2M", "D7", "D8"),
    ("R18", "1.1M", "D8", "GND"),
]

# F.Cu = K, In1..In8 = signals, B.Cu = GND
LAYER_STACK = [("F.Cu", None)]
for i in range(1, 9):
    LAYER_STACK.append((f"In{i}.Cu", f"Jumper{i}"))
LAYER_STACK.append(("B.Cu", None))
POWER_LAYER = {"K": 0, "GND": len(LAYER_STACK) - 1}

W_PWR = 0.60
W_SIG = 0.35


def uid(name: str) -> str:
    return str(uuid.uuid5(SHEET, name))


def snap(v: float) -> float:
    return round(v / G) * G


def same_pt(a, b, tol=0.05) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def rot_xy(px: float, py: float, deg: float) -> tuple[float, float]:
    rad = math.radians(-deg)
    return (
        px * math.cos(rad) - py * math.sin(rad),
        px * math.sin(rad) + py * math.cos(rad),
    )


def world_pad(fx: float, fy: float, rot: float, lx: float, ly: float) -> tuple[float, float]:
    dx, dy = rot_xy(lx, ly, rot)
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
) -> str:
    mod = inject_pad_nets(mod_text, pad_nets, ref)
    mod = hide_fp_silk_text(mod)
    mod = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', mod, count=1)
    mod = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{value}"', mod, count=1)
    body = indent_body(mod, 2)
    return f"""\t(footprint "{lib_id}"
\t\t(layer "F.Cu")
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


def path_pts(
    name: str, pts: list[tuple[float, float]], width: float, layer: str, net_id: int
) -> list[str]:
    out: list[str] = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if same_pt(a, b):
            continue
        out.append(segment(f"{name}-{i}", a[0], a[1], b[0], b[1], width, layer, net_id))
    return out


def seg_hits_pad(a, b, pads, net, ends) -> bool:
    ax, ay = a
    bx, by = b
    for px, py, pnet in pads:
        if pnet == net:
            continue
        if any(same_pt((px, py), e, HIT) for e in ends):
            continue
        if abs(ay - by) < 1e-6:
            if abs(py - ay) > HIT:
                continue
            lo, hi = (ax, bx) if ax <= bx else (bx, ax)
            if lo - HIT <= px <= hi + HIT:
                return True
        elif abs(ax - bx) < 1e-6:
            if abs(px - ax) > HIT:
                continue
            lo, hi = (ay, by) if ay <= by else (by, ay)
            if lo - HIT <= py <= hi + HIT:
                return True
    return False


def path_blocked(pts, net, pads) -> bool:
    ends = [pts[0], pts[-1]]
    for p1, p2 in zip(pts, pts[1:]):
        if same_pt(p1, p2):
            continue
        if seg_hits_pad(p1, p2, pads, net, ends):
            return True
    return False


def grid_vals(v0, v1, origin, extra=6):
    lo, hi = (v0, v1) if v0 <= v1 else (v1, v0)
    start = origin + round((lo - origin) / G) * G - extra * G
    stop = origin + round((hi - origin) / G) * G + extra * G
    vals = []
    v = start
    while v <= stop + 1e-9:
        vals.append(round(v, 4))
        v += G
    return vals


def manhattan_path(a, b, net, pads, ox, oy):
    ax, ay = a
    bx, by = b
    candidates: list[list[tuple[float, float]]] = []
    if abs(ax - bx) < 1e-6 or abs(ay - by) < 1e-6:
        candidates.append([a, b])
    candidates.append([a, (bx, ay), b])
    candidates.append([a, (ax, by), b])
    for x in grid_vals(ax, bx, ox):
        if abs(x - ax) < 0.4 or abs(x - bx) < 0.4:
            continue
        candidates.append([a, (x, ay), (x, by), b])
    for y in grid_vals(ay, by, oy):
        if abs(y - ay) < 0.4 or abs(y - by) < 0.4:
            continue
        candidates.append([a, (ax, y), (bx, y), b])
    for sx in (-G, G, -2 * G, 2 * G, -3 * G, 3 * G, -4 * G, 4 * G):
        for sy in (-G, G, -2 * G, 2 * G, -3 * G, 3 * G):
            candidates.append([a, (ax + sx, ay), (ax + sx, by + sy), (bx, by + sy), b])
            candidates.append([a, (ax, ay + sy), (bx + sx, ay + sy), (bx + sx, by), b])

    def score(pts):
        length = 0.0
        segs = 0
        for p1, p2 in zip(pts, pts[1:]):
            if same_pt(p1, p2):
                continue
            segs += 1
            length += abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        return (segs, length)

    clear = [p for p in candidates if not path_blocked(p, net, pads)]
    if clear:
        clear.sort(key=score)
        return clear[0]
    candidates.sort(key=score)
    print(f"  warn: no clear path for {net} {a} -> {b}")
    return candidates[0]


def polyline_segs(pts):
    return [(p1, p2) for p1, p2 in zip(pts, pts[1:]) if not same_pt(p1, p2)]


def segs_cross(p1, p2, q1, q2) -> bool:
    if any(same_pt(u, v) for u in (p1, p2) for v in (q1, q2)):
        return False

    def side(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 1 if v > 0 else (-1 if v < 0 else 0)

    s1, s2 = side(p1, p2, q1), side(p1, p2, q2)
    s3, s4 = side(q1, q2, p1), side(q1, q2, p2)
    if 0 in (s1, s2, s3, s4):
        return False
    return s1 != s2 and s3 != s4


def collinear_overlap(p1, p2, q1, q2, tol=0.2) -> bool:
    def iv(a0, a1, b0, b1):
        lo_a, hi_a = (a0, a1) if a0 <= a1 else (a1, a0)
        lo_b, hi_b = (b0, b1) if b0 <= b1 else (b1, b0)
        return lo_a < hi_b - tol and lo_b < hi_a - tol

    if abs(p1[1] - p2[1]) <= tol and abs(q1[1] - q2[1]) <= tol and abs(p1[1] - q1[1]) <= tol:
        return iv(p1[0], p2[0], q1[0], q2[0])
    if abs(p1[0] - p2[0]) <= tol and abs(q1[0] - q2[0]) <= tol and abs(p1[0] - q1[0]) <= tol:
        return iv(p1[1], p2[1], q1[1], q2[1])
    return False


def conflict(path_a, path_b) -> bool:
    for p1, p2 in polyline_segs(path_a):
        for q1, q2 in polyline_segs(path_b):
            if segs_cross(p1, p2, q1, q2) or collinear_overlap(p1, p2, q1, q2):
                return True
    return False


def color_layers(paths: list[tuple[str, list]]) -> dict[int, int]:
    """Assign signal paths to InN indices (1..8); greedy conflict coloring."""
    assign: dict[int, int] = {}
    for i, (_net, pts) in enumerate(paths):
        used = set()
        for j, layer_i in assign.items():
            if conflict(pts, paths[j][1]):
                used.add(layer_i)
        for cand in range(1, 9):
            if cand not in used:
                assign[i] = cand
                break
        else:
            assign[i] = 1
            print(f"  warn: layer stack exhausted for path {i}")
    return assign


def mst_edges(pts: list[tuple[float, float]]) -> list[tuple[int, int]]:
    n = len(pts)
    if n < 2:
        return []
    in_t = {0}
    edges: list[tuple[int, int]] = []
    while len(in_t) < n:
        best = None
        for i in in_t:
            for j in range(n):
                if j in in_t:
                    continue
                d = abs(pts[i][0] - pts[j][0]) + abs(pts[i][1] - pts[j][1])
                if best is None or d < best[0]:
                    best = (d, i, j)
        assert best is not None
        _, i, j = best
        edges.append((i, j))
        in_t.add(j)
    return edges


def build_pcb() -> str:
    r_mod = load_mod(
        KICAD_FP
        / "Resistor_THT.pretty"
        / "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.kicad_mod"
    )
    j3_mod = load_mod(
        KICAD_FP
        / "TerminalBlock_Phoenix.pretty"
        / "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal.kicad_mod"
    )
    j4_mod = load_mod(PRETTY / "HDR_2x7_IC_Socket.kicad_mod")
    j5_mod = load_mod(
        KICAD_FP / "Connector_Coaxial.pretty" / "BNC_TEConnectivity_1478204_Vertical.kicad_mod"
    )
    jmp_mod = load_mod(
        KICAD_FP / "Connector_PinHeader_2.54mm.pretty" / "PinHeader_1x02_P2.54mm_Vertical.kicad_mod"
    )
    c_mod = load_mod(
        KICAD_FP / "Capacitor_THT.pretty" / "C_Disc_D5.0mm_W2.5mm_P5.00mm.kicad_mod"
    )

    # --- Gate 6: snapped placement (same as Gate 5-cleared draft) ---
    j3_x, j3_y = snap(X0 + 15), snap(Y0 + 20)
    bleed_x, bleed_y = snap(j3_x + 20), snap(j3_y + 20)
    div_x = snap(X0 + 50)
    r0_y = snap(Y0 + 25)
    pitch = 15.24
    j4_x, j4_y = snap(X0 + 100), snap(Y0 + 80)
    a_x, a_y = snap(X0 + 100), snap(Y0 + 25)
    r19_x, r19_y = snap(a_x - 18), a_y
    jmp_x, jmp_y = snap(a_x - 18), snap(a_y + 10)
    c4_x, c4_y = snap(a_x - 18), snap(a_y + 20)

    fps: list[str] = []
    pads: list[tuple[float, float, str]] = []  # world pads for keep-out
    by_net: dict[str, list[tuple[float, float]]] = {n: [] for n in NET_NAMES if n}

    def add_pad(net: str, xy: tuple[float, float]) -> None:
        if not net:
            return
        pads.append((xy[0], xy[1], net))
        by_net[net].append(xy)

    def place(lib, mod, ref, val, x, y, rot, pad_nets_local, local_pads):
        pn = {p: (NID[n], n) for p, n in pad_nets_local.items()}
        fps.append(place_footprint(lib, mod, ref, val, x, y, rot, pn))
        for pnum, (lx, ly) in local_pads.items():
            net = pad_nets_local.get(pnum, "")
            add_pad(net, world_pad(x, y, rot, lx, ly))

    # Axial P10.16: pad1 at origin (0,0), pad2 at (10.16,0) — not ±half from center.
    r_pads = {"1": (0.0, 0.0), "2": (10.16, 0.0)}
    place(
        "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        j3_mod,
        "J3",
        "HV_IN",
        j3_x,
        j3_y,
        0,
        {"1": "K", "2": "GND"},
        {"1": (0, 0), "2": (5.08, 0)},
    )
    place(
        "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        r_mod,
        "Rbleed",
        "22M",
        bleed_x,
        bleed_y,
        270,
        {"1": "K", "2": "GND"},
        r_pads,
    )
    for i, (ref, val, n1, n2) in enumerate(DIVIDER):
        y = snap(r0_y + i * pitch)
        place(
            "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
            r_mod,
            ref,
            val,
            div_x,
            y,
            270,
            {"1": n1, "2": n2},
            r_pads,
        )

    j4_local = {
        "1": (-3.81, 7.62),
        "2": (-3.81, 5.08),
        "3": (-3.81, 2.54),
        "4": (-3.81, 0.0),
        "5": (-3.81, -2.54),
        "6": (-3.81, -5.08),
        "7": (-3.81, -7.62),
        "8": (3.81, -7.62),
        "9": (3.81, -5.08),
        "10": (3.81, -2.54),
        "11": (3.81, 0.0),
        "12": (3.81, 2.54),
        "13": (3.81, 5.08),
        "14": (3.81, 7.62),
    }
    place(
        "XP3312:HDR_2x7_IC_Socket",
        j4_mod,
        "J4",
        "MATE_J1",
        j4_x,
        j4_y,
        0,
        J4_NET,
        {p: j4_local[p] for p in J4_NET},
    )
    # NC pads still need keep-out
    for p in ("1", "10", "11", "13"):
        pads.append((*world_pad(j4_x, j4_y, 0, *j4_local[p]), ""))

    place(
        "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        r_mod,
        "R19",
        "47R",
        r19_x,
        r19_y,
        0,
        {"1": "A", "2": "SCOPE"},
        r_pads,
    )
    place(
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        jmp_mod,
        "JMP_DC",
        "DC_COUPLE",
        jmp_x,
        jmp_y,
        90,
        {"1": "A", "2": "SCOPE"},
        {"1": (0, 0), "2": (0, 2.54)},
    )
    place(
        "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
        c_mod,
        "C4",
        "1nF",
        c4_x,
        c4_y,
        90,
        {"1": "A", "2": "SCOPE"},
        {"1": (0, 0), "2": (5.0, 0)},
    )
    place(
        "Connector_Coaxial:BNC_TEConnectivity_1478204_Vertical",
        j5_mod,
        "J5",
        "BNC_SCOPE",
        a_x,
        a_y,
        0,
        {"1": "SCOPE", "2": "GND"},
        {"1": (0, 0), "2": (-3.175, -3.175)},  # one shell pad is enough for net membership
    )
    # Extra J5 shell pads for keep-out / GND stitch
    for lx, ly in ((-3.175, 3.175), (3.175, -3.175), (3.175, 3.175)):
        add_pad("GND", world_pad(a_x, a_y, 0, lx, ly))

    # --- Gates 7–8: route ---
    segs: list[str] = []
    ox, oy = j3_x, j3_y  # grid origin = J3 pad 1 (K)

    def route_net(net: str, layer_name: str, width: float) -> None:
        pts = by_net[net]
        # unique within 0.1 mm
        uniq: list[tuple[float, float]] = []
        for p in pts:
            if not any(same_pt(p, u, 0.15) for u in uniq):
                uniq.append(p)
        if len(uniq) < 2:
            return
        for ia, ib in mst_edges(uniq):
            path = manhattan_path(uniq[ia], uniq[ib], net, pads, ox, oy)
            segs.extend(path_pts(f"{net}-{ia}-{ib}", path, width, layer_name, NID[net]))

    # Power on dedicated layers
    route_net("K", "F.Cu", W_PWR)
    route_net("GND", "B.Cu", W_PWR)

    # Signals: build paths then conflict-color onto InN
    sig_nets = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "A", "SCOPE"]
    signal_paths: list[tuple[str, list]] = []
    for net in sig_nets:
        pts = by_net[net]
        uniq: list[tuple[float, float]] = []
        for p in pts:
            if not any(same_pt(p, u, 0.15) for u in uniq):
                uniq.append(p)
        if len(uniq) < 2:
            continue
        for ia, ib in mst_edges(uniq):
            path = manhattan_path(uniq[ia], uniq[ib], net, pads, ox, oy)
            signal_paths.append((net, path))

    layer_of = color_layers(signal_paths)
    for i, (net, path) in enumerate(signal_paths):
        li = layer_of[i]
        layer_name = LAYER_STACK[li][0]
        segs.extend(path_pts(f"{net}-s{i}", path, W_SIG, layer_name, NID[net]))

    nets_sexpr = "\n".join(
        f'\t(net {i} "{n}")' if n else '\t(net 0 "")' for i, n in enumerate(NET_NAMES)
    )

    copper_layers = []
    for idx, (name, user) in enumerate(LAYER_STACK):
        # Traditional KiCad: F.Cu=0 … InN … B.Cu=31
        lid = 31 if name == "B.Cu" else idx
        if user:
            copper_layers.append(f'\t\t({lid} "{name}" signal "{user}")')
        else:
            copper_layers.append(f'\t\t({lid} "{name}" signal)')
    layer_block = "\n".join(
        copper_layers
        + [
            '\t\t(32 "B.Adhes" user "B.Adhesive")',
            '\t\t(33 "F.Adhes" user "F.Adhesive")',
            '\t\t(34 "B.Paste" user)',
            '\t\t(35 "F.Paste" user)',
            '\t\t(36 "B.SilkS" user "B.Silkscreen")',
            '\t\t(37 "F.SilkS" user "F.Silkscreen")',
            '\t\t(38 "B.Mask" user)',
            '\t\t(39 "F.Mask" user)',
            '\t\t(40 "Dwgs.User" user "User.Drawings")',
            '\t\t(41 "Cmts.User" user "User.Comments")',
            '\t\t(42 "Eco1.User" user "User.Eco1")',
            '\t\t(43 "Eco2.User" user "User.Eco2")',
            '\t\t(44 "Edge.Cuts" user)',
            '\t\t(45 "Margin" user)',
            '\t\t(46 "B.CrtYd" user "B.Courtyard")',
            '\t\t(47 "F.CrtYd" user "F.Courtyard")',
            '\t\t(48 "B.Fab" user "B.Fabrication")',
            '\t\t(49 "F.Fab" user "F.Fabrication")',
        ]
    )
    edge = f"""\t(gr_rect
\t\t(start {X0:.2f} {Y0:.2f})
\t\t(end {X0 + W:.2f} {Y0 + H:.2f})
\t\t(stroke (width 0.1) (type solid))
\t\t(fill none)
\t\t(layer "Edge.Cuts")
\t\t(uuid "{uid("edge")}")
\t)"""

    notes = f"""\t(gr_text "bringup-supply PCB — Gates 6–9 routed\\nF.Cu=K(-HV) B.Cu=GND InN=dynode/A/SCOPE\\nGate 5 placement OK; STOP for Gate 10 operator"
\t\t(at {snap(X0 + 5)} {snap(Y0 + H - 8)} 0)
\t\t(layer "Cmts.User")
\t\t(uuid "{uid("note")}")
\t\t(effects (font (size 1.2 1.2) (thickness 0.18)) (justify left bottom))
\t)"""

    return f"""(kicad_pcb
\t(version 20241229)
\t(generator "gen_bringup_pcb.py")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "bringup-supply")
\t\t(date "2026-11-02")
\t\t(rev "0.2-route")
\t\t(comment 1 "Type A HV divider + anode — routed after Gate 5")
\t\t(comment 2 "F.Cu=K B.Cu=GND InN=signals; awaiting Gate 10 operator")
\t)
\t(layers
{layer_block}
\t)
\t(setup
\t\t(pad_to_mask_clearance 0.0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t)
{nets_sexpr}
{notes}
{edge}
{chr(10).join(fps)}
{chr(10).join(segs)}
)
"""


def parse_footprints(text: str) -> list[dict]:
    fps: list[dict] = []
    parts = re.split(r"\n\t\(footprint ", text)
    for chunk in parts[1:]:
        body = "(footprint " + chunk
        depth = 0
        end = None
        for i, ch in enumerate(body):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        fp = body[:end]
        ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
        at_m = re.search(r"\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", fp)
        if not ref_m or not at_m:
            continue
        pads: dict[str, tuple[float, float, str]] = {}
        for pm in re.finditer(
            r'\(pad "([^"]+)"[\s\S]*?\n[ \t]+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)',
            fp,
        ):
            num = pm.group(1)
            lx, ly = float(pm.group(2)), float(pm.group(3))
            # Bound the pad body so NC pads do not inherit the next pad's net
            rest = fp[pm.start() :]
            depth = 0
            end = len(rest)
            for i, ch in enumerate(rest):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            sub = rest[:end]
            # KiCad may write (net N "NAME") or (net "NAME") after Pcbnew save
            nm = re.search(r'\(net (?:\d+ )?"([^"]+)"\)', sub)
            net = nm.group(1) if nm else ""
            # Keep first pad number for connectivity key; extras stored as num#k
            key = num
            k = 2
            while key in pads:
                key = f"{num}#{k}"
                k += 1
            pads[key] = (lx, ly, net)
        fps.append(
            {
                "ref": ref_m.group(1),
                "x": float(at_m.group(1)),
                "y": float(at_m.group(2)),
                "rot": float(at_m.group(3) or 0),
                "pads": pads,
                "raw": fp,
            }
        )
    return fps


def set_fp_at(fp_raw: str, x: float, y: float, rot: float) -> str:
    if abs(rot) < 1e-9:
        repl = f"(at {x:.4f} {y:.4f})"
    else:
        repl = f"(at {x:.4f} {y:.4f} {rot:g})"
    return re.sub(
        r"\n\t\t\(at [-\d.]+ [-\d.]+(?: [-\d.]+)?\)",
        "\n\t\t" + repl,
        fp_raw,
        count=1,
    )


def strip_segments(text: str) -> str:
    return re.sub(r"\n\t\(segment\b[\s\S]*?\n\t\)", "", text)


def snap_tracked_pcb() -> None:
    """Gate 6: snap XY to 2.54 mm; snap rotation to 90°. Preserve operator layout."""
    if not OUT.is_file():
        raise SystemExit(f"missing tracked PCB: {OUT}")
    text = OUT.read_text()
    fps = parse_footprints(text)
    if not fps:
        raise SystemExit("no footprints in tracked PCB")
    origin = next((f for f in fps if f["ref"] == "J3"), fps[0])
    ox, oy = origin["x"], origin["y"]
    print(f"snap origin {origin['ref']} ({ox}, {oy})")
    for f in fps:
        sx = ox + round((f["x"] - ox) / G) * G
        sy = oy + round((f["y"] - oy) / G) * G
        srot = round(f["rot"] / 90.0) * 90.0
        print(
            f"  {f['ref']:7} ({f['x']:8.3f},{f['y']:8.3f}) r={f['rot']:7.2f} "
            f"-> ({sx:.3f},{sy:.3f}) r={srot:g}"
        )
        new_raw = set_fp_at(f["raw"], sx, sy, srot)
        if f["raw"] not in text:
            raise SystemExit(f"failed to locate footprint block for {f['ref']}")
        text = text.replace(f["raw"], new_raw, 1)
    text = strip_segments(text)
    text = re.sub(r'\(rev "[^"]*"\)', '(rev "0.3-snap")', text, count=1)
    OUT.write_text(text)
    print("wrote", OUT, "— snapped; copper cleared; run --route then DRC")


def ensure_net_table(text: str) -> str:
    """Ensure (net N "name") table exists (Pcbnew may omit codes on pads only)."""
    nets_block = "\n".join(
        f'\t(net {i} "{n}")' if n else '\t(net 0 "")' for i, n in enumerate(NET_NAMES)
    )
    if re.search(r'\n\t\(net 0 ""\)', text) or re.search(r'\n\t\(net 1 "GND"\)', text):
        return text
    # Insert after setup block if present, else after (layers …)
    m = re.search(r"\n\t\(setup\b[\s\S]*?\n\t\)", text)
    if m:
        return text[: m.end()] + "\n" + nets_block + text[m.end() :]
    m = re.search(r"\n\t\(layers\b[\s\S]*?\n\t\)", text)
    if m:
        return text[: m.end()] + "\n" + nets_block + text[m.end() :]
    return text


def normalize_pad_nets(text: str) -> str:
    """Rewrite (net "NAME") → (net CODE "NAME") for known nets."""

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in NID:
            return f'(net {NID[name]} "{name}")'
        return m.group(0)

    return re.sub(r'\(net "([^"]+)"\)', repl, text)


def route_tracked_pcb() -> None:
    """Gates 7–8: route using footprint positions already in the tracked PCB."""
    if not OUT.is_file():
        raise SystemExit(f"missing tracked PCB: {OUT}")
    text = OUT.read_text()
    text = ensure_net_table(text)
    text = normalize_pad_nets(text)
    fps = parse_footprints(text)
    if not fps:
        raise SystemExit("no footprints in tracked PCB")

    pads: list[tuple[float, float, str]] = []
    by_net: dict[str, list[tuple[float, float]]] = {n: [] for n in NET_NAMES if n}

    def add_pad(net: str, xy: tuple[float, float]) -> None:
        if not net or net not in by_net:
            return
        pads.append((xy[0], xy[1], net))
        by_net[net].append(xy)

    for f in fps:
        for num, (lx, ly, net) in f["pads"].items():
            # Canonical J4 wrap map — ignore any Pcbnew mis-assignment on NC pins
            if f["ref"] == "J4":
                base = num.split("#", 1)[0]
                net = J4_NET.get(base, "")
                f["pads"][num] = (lx, ly, net)
            # BNC shell pads are all "2" — force GND
            if f["ref"] == "J5" and num.split("#", 1)[0] == "2":
                net = "GND"
                f["pads"][num] = (lx, ly, net)
            wx, wy = world_pad(f["x"], f["y"], f["rot"], lx, ly)
            add_pad(net, (wx, wy))
            if not net:
                pads.append((wx, wy, ""))

    for net, pts in by_net.items():
        print(f"  net {net}: {len(pts)} pads")

    origin = next((f for f in fps if f["ref"] == "J3"), fps[0])
    ox, oy = origin["x"], origin["y"]
    segs: list[str] = []

    def route_net(net: str, layer_name: str, width: float) -> None:
        pts = by_net[net]
        uniq: list[tuple[float, float]] = []
        for p in pts:
            if not any(same_pt(p, u, 0.15) for u in uniq):
                uniq.append(p)
        if len(uniq) < 2:
            return
        for ia, ib in mst_edges(uniq):
            path = manhattan_path(uniq[ia], uniq[ib], net, pads, ox, oy)
            segs.extend(path_pts(f"{net}-{ia}-{ib}", path, width, layer_name, NID[net]))

    route_net("K", "F.Cu", W_PWR)
    route_net("GND", "B.Cu", W_PWR)

    sig_nets = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "A", "SCOPE"]
    signal_paths: list[tuple[str, list]] = []
    for net in sig_nets:
        pts = by_net[net]
        uniq: list[tuple[float, float]] = []
        for p in pts:
            if not any(same_pt(p, u, 0.15) for u in uniq):
                uniq.append(p)
        if len(uniq) < 2:
            continue
        for ia, ib in mst_edges(uniq):
            path = manhattan_path(uniq[ia], uniq[ib], net, pads, ox, oy)
            signal_paths.append((net, path))
    layer_of = color_layers(signal_paths)
    for i, (net, path) in enumerate(signal_paths):
        li = layer_of[i]
        layer_name = LAYER_STACK[li][0]
        segs.extend(path_pts(f"{net}-s{i}", path, W_SIG, layer_name, NID[net]))

    if not segs:
        raise SystemExit("route produced 0 segments — pad nets missing or unreadable")

    text = strip_segments(text)
    insert = "\n" + "\n".join(segs) + "\n"
    text = re.sub(r"\n\)\s*$", insert + ")\n", text, count=1)
    text = re.sub(r'\(rev "[^"]*"\)', '(rev "0.4-route")', text, count=1)
    OUT.write_text(text)
    print("wrote", OUT, f"— {len(segs)} segments from tracked placement")
    print("run: kicad-cli pcb drc … then STOP for Gate 10")


def main() -> None:
    import sys

    argv = sys.argv[1:]
    if "--snap" in argv:
        snap_tracked_pcb()
        return
    if "--route" in argv:
        route_tracked_pcb()
        return
    if "--force-place" in argv:
        text = build_pcb()
        OUT.write_text(text)
        print("wrote", OUT, "(forced placement draft — operator must re-do Gate 5)")
        return
    if OUT.is_file():
        raise SystemExit(
            f"refusing to overwrite tracked {OUT}\n"
            "  After Gate 5, use --snap then --route (preserves placement/rotation).\n"
            "  Use --force-place only when the operator asks to discard placement."
        )
    text = build_pcb()
    OUT.write_text(text)
    print("wrote", OUT, "— initial Gate 4 draft; STOP for Gate 5")


if __name__ == "__main__":
    main()
