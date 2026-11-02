#!/usr/bin/env python3
"""Generate XP3312 circular flying-lead footprint + a mapping PCB."""

from __future__ import annotations

from pathlib import Path

from tube_geo import (
    FP_DRILL_MM,
    FP_GUIDE_DIA_MM,
    FP_PAD_DIA_MM,
    FP_PIN_CIRCLE_DIA_MM,
    pin_positions,
)

ROOT = Path(__file__).resolve().parent
PRETTY = ROOT / "libraries" / "XP3312.pretty"
PROJECT = "pmt-interface"


def footprint() -> str:
    r = FP_PIN_CIRCLE_DIA_MM / 2.0
    pads = []
    silk = []
    for p in pin_positions(r):
        pads.append(
            f"""\t(pad "{p.number}" thru_hole circle
\t\t(at {p.x:.4f} {p.y:.4f})
\t\t(size {FP_PAD_DIA_MM} {FP_PAD_DIA_MM})
\t\t(drill {FP_DRILL_MM})
\t\t(layers "*.Cu" "*.Mask")
\t\t(remove_unused_layers no)
\t)"""
        )
        lx = p.x * 1.22
        ly = p.y * 1.22
        label = p.name if p.name != "ic" else p.number
        silk.append(
            f"""\t(fp_text user "{label}"
\t\t(at {lx:.4f} {ly:.4f} 0)
\t\t(layer "F.SilkS")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.12)
\t\t\t)
\t\t)
\t)"""
        )

    guide_r = FP_GUIDE_DIA_MM / 2.0
    return f"""(footprint "XP3312_FlyingLead"
\t(version 20260206)
\t(generator "gen_fp.py")
\t(layer "F.Cu")
\t(descr "Photonis XP3312 flying-lead / plastic retainer pin circle (datasheet 31.8mm). View = pins facing you; SP south; 1..19 clockwise.")
\t(tags "PMT XP3312 Photonis photomultiplier flying-lead")
\t(property "Reference" "U**"
\t\t(at 0 {-(r + 6):.2f} 0)
\t\t(layer "F.SilkS")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1 1)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(property "Value" "XP3312_FlyingLead"
\t\t(at 0 {r + 6:.2f} 0)
\t\t(layer "F.Fab")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1 1)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(property "Datasheet" "docs/datasheets/XP3312.pdf"
\t\t(at 0 0 0)
\t\t(layer "F.Fab")
\t\t(hide yes)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1 1)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(attr through_hole)
\t(fp_circle
\t\t(center 0 0)
\t\t(end {r:.4f} 0)
\t\t(stroke
\t\t\t(width 0.12)
\t\t\t(type solid)
\t\t)
\t\t(layer "F.SilkS")
\t\t(fill none)
\t)
\t(fp_circle
\t\t(center 0 0)
\t\t(end {guide_r:.4f} 0)
\t\t(stroke
\t\t\t(width 0.12)
\t\t\t(type solid)
\t\t)
\t\t(layer "F.SilkS")
\t\t(fill none)
\t)
\t(fp_circle
\t\t(center 0 0)
\t\t(end {r + 1.5:.4f} 0)
\t\t(stroke
\t\t\t(width 0.05)
\t\t\t(type solid)
\t\t)
\t\t(layer "F.CrtYd")
\t\t(fill none)
\t)
\t(fp_text user "SP"
\t\t(at 0 {-r - 3.5:.2f} 0)
\t\t(layer "F.SilkS")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1 1)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
{chr(10).join(pads)}
{chr(10).join(silk)}
\t(embedded_fonts no)
)
"""


def _indent_footprint(mod_text: str, spaces: int = 2) -> str:
    """Strip outer (footprint …) wrapper and re-indent body for PCB placement."""
    lines = mod_text.strip().splitlines()
    # drop first "(footprint …" and last ")"
    body = lines[1:-1]
    pad = " " * spaces
    return "\n".join(pad + ln if ln else ln for ln in body)


def pcb_with_embedded_fp(mod_text: str) -> str:
    """Minimal PCB with one inlined tube footprint for physical pin mapping."""
    body = _indent_footprint(mod_text, 2)
    # Override reference/value and set board position
    body = body.replace('(property "Reference" "U**"', '(property "Reference" "U1"', 1)
    body = body.replace(
        '(property "Value" "XP3312_FlyingLead"',
        '(property "Value" "XP3312/SQ"',
        1,
    )
    return f"""(kicad_pcb
\t(version 20241229)
\t(generator "gen_fp.py")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "pmt-interface tube map")
\t\t(date "2026-10-31")
\t\t(rev "0.1")
\t\t(comment 1 "XP3312 flying-lead pin circle for continuity / symbol mapping")
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
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t)
\t(net 0 "")
\t(gr_text "XP3312 pin map (pins facing you)\\nSP at south; 1..19 clockwise\\nMatches schematic symbol + datasheet"
\t\t(at 105 28 0)
\t\t(layer "Cmts.User")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.5 1.5)
\t\t\t\t(thickness 0.2)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "a1111111-1111-4111-8111-111111111111")
\t)
\t(gr_rect
\t\t(start 70 40)
\t\t(end 140 110)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "Edge.Cuts")
\t\t(uuid "a2222222-2222-4222-8222-222222222222")
\t)
\t(footprint "XP3312:XP3312_FlyingLead"
\t\t(layer "F.Cu")
\t\t(uuid "a3333333-3333-4333-8333-333333333333")
\t\t(at 105 75)
{body}
\t)
)
"""


def main() -> None:
    PRETTY.mkdir(parents=True, exist_ok=True)
    mod_text = footprint()
    mod = PRETTY / "XP3312_FlyingLead.kicad_mod"
    mod.write_text(mod_text)
    print("wrote", mod)

    fp_table = ROOT / "fp-lib-table"
    fp_table.write_text(
        """(fp_lib_table
  (version 7)
  (lib (name "XP3312")(type "KiCad")(uri "${KIPRJMOD}/libraries/XP3312.pretty")(options "")(descr "XP3312 tube footprints"))
)
"""
    )
    print("wrote", fp_table)

    # Full photo-matched filter PCB is produced by gen_pcb.py (not the pin-map stub).
    print("tube footprint only; run gen_pcb.py for the filter PCB")


if __name__ == "__main__":
    main()
