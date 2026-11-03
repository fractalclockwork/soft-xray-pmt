---
name: kicad-schematic-routing
description: >-
  KiCad schematic wire routing with orthogonal and diagonal segments, and
  crossings that do not create junctions (multi-layer style). Use when editing
  or generating KiCad .kicad_sch files, drawing wires around circular symbols,
  or when the user asks for diagonal wires, 45-degree routes, or non-joining
  wire crossings.
disable-model-invocation: false
---

# KiCad schematic routing (orthogonal + diagonal, cross without junction)

## Goals

1. Wires may run **horizontal, vertical, or diagonal** (typically 45°, any angle when mapping circular pinouts).
2. Wires may **cross without joining** — treat a visual cross as different “layers” unless a junction is intentional.
3. Prefer clarity when fanning out from **circular tube/connector symbols** to Manhattan buses.

## KiCad behavior (do not fight it)

- A **junction** is created only at a shared vertex / explicit junction object — two segments that merely cross mid-span are **not** connected.
- Do **not** place `(junction …)` where wires only cross.
- Place a junction only for intentional T-joins or three-or-more net meetings.
- Crossing without connecting is the correct way to mimic multi-layer PCB routing on a schematic.

## When generating `.kicad_sch` (S-expression)

### Multi-point wires (preferred)

Emit one wire object per segment, or a chain of segments. Diagonals are normal `(wire (pts (xy x1 y1) (xy x2 y2)) …)` with unequal Δx and Δy:

```scheme
(wire
  (pts
    (xy 50.8 40.64)
    (xy 63.5 53.34)
  )
  (stroke
    (width 0)
    (type default)
  )
  (uuid "…")
)
```

### Routing recipe around circular symbols

1. Leave the pin tip at the circle.
2. Take a short **radial** stub (along the pin angle) or a short diagonal to clear the body.
3. Join a **bus** with orthogonal and/or 45° segments.
4. Allow buses to **cross** dynode fans; use **net labels** at both ends if a long run is hard to follow — labels connect nets without a drawn join.

### Helper pattern (Python)

```python
def wire_seg(name, a, b):
    # a, b are (x, y); diagonal allowed whenever ax!=bx and ay!=by
    ...

def wire_path(name, points):
    for i, (a, b) in enumerate(zip(points, points[1:])):
        wire_seg(f"{name}-{i}", a, b)
```

Prefer 45° when possible: choose intermediate points so `|Δx| == |Δy|` on diagonal legs.

### What not to do

- Do not force every net through only H/V if that obscures a circular pin map.
- Do not add junctions at crossings “to be safe” — that **shorts** nets.
- Do not use overlapping collinear endpoints for unrelated nets.
- Do **not** route many nets onto one shared bus **column/row** with Manhattan stubs — an endpoint that lands mid-segment is a **T-join** and shorts nets. Prefer **net labels** at each end, or unique X/Y channels per net, or pure mid-span diagonals that never share vertices.
- On dual-row headers, stub labels **outward** from each pin — stubs toward the connector center on the same row will overlap and short left/right pins.
- J1 is a **wide IC-style 2×7 wrap socket** (left `1–7` top→bottom, right `14–8`), not IDC Odd/Even ribbon numbering. Same geometry as Prutchi Fig. 3.
- Place discrete parts on the **1.27 mm** schematic grid (`snap` / `snap_pt` in `gen_sch.py`).
- Do not place the same net label on **both sides** of a series resistor (that bypasses the R).

## When editing in the KiCad GUI

1. **Wire tool**: click–click; hold modifiers per KiCad version for 45° / any-angle (KiCad 8+/10: constrain modes in the bottom status / preferences → Schematic Editor → Editing → “Constrain wires / radials”).
2. To cross without joining: draw through; ensure no junction dot appears.
3. If a junction appears wrongly: delete the junction object; confirm nets in the net navigator.
4. For circular symbols: route radial stubs first, then 45° into the bus.

## Project conventions (soft-xray-pmt)

- Tube symbol pins follow the **PCB footprint circle** (`tube_geo.py`): SP south, 1..19 clockwise, pins facing you.
- Schematic pin **tips** sit on that circle; pin **orientation** is snapped to 0/90/180/270 (`outward_pin_angle`) — KiCad rejects non-cardinal pin angles on load.
- Regenerators: `hardware/pmt-interface/gen_sch.py`, `gen_fp.py`.
- After changing circular geometry, regenerate schematic **and** footprint so symbol ↔ footprint stay mapped.

## Checklist before finishing a schematic edit

- [ ] Intentional joins have junctions; crossings do not
- [ ] Circular pin order matches datasheet / footprint
- [ ] ERC: no unexpected `pin_not_connected` on routed electrodes
- [ ] Diagonal segments used where they shorten radial fan-out
