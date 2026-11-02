# XP3312 circular pin map (symbol ↔ footprint)

Shared geometry lives in [`hardware/pmt-interface/tube_geo.py`](../hardware/pmt-interface/tube_geo.py). Regenerators: `gen_sch.py` (circular schematic symbol) and `gen_fp.py` (footprint + mapping PCB).

## View convention

- Looking **from the bottom of the tube up** (pins facing you) — continuity-confirmed vs board (D1→J1.8, K→J1.7)
- **SP** (short pin / key) at **south**
- Numbered pins **1 … 19 clockwise** at **18°** spacing (20 positions total)
- Footprint pin circle diameter **31.8 mm** (datasheet flying-lead outline)
- Schematic uses a larger circle (radius 22.86 mm) so electrode names stay readable; **angles and numbers match the footprint**

## Electrode ↔ pad number

| Pad | Electrode | Notes |
|-----|-----------|--------|
| SP | SP | Key / short pin; schematic type `unconnected` |
| 1 | D1 | |
| 2 | ic | Internal connection / unused on stock board |
| 3 | D2 | |
| 4 | D3 | |
| 5 | ic | |
| 6 | ic | |
| 7 | D4 | |
| 8 | D5 | |
| 9 | D6 | |
| 10 | D7 | Last-dynode bypass (C2) |
| 11 | D8 | Last-dynode bypass (C3) |
| 12 | A | Anode → coax + R2 |
| 13 | ic | |
| 14 | ic | |
| 15 | ic | |
| 16 | K | Cathode → R1 / C1 |
| 17 | ic | |
| 18 | ic | |
| 19 | ic | |

Source: Photonis XP3312 outline / Prutchi Fig. 4 (see [`docs/datasheets/`](datasheets/), [`docs/pin-reconciliation.md`](pin-reconciliation.md)).

## Files

| Artifact | Path |
|----------|------|
| Symbol (embedded in sch + lib) | `hardware/pmt-interface/libraries/XP3312.kicad_sym` |
| Footprint | `hardware/pmt-interface/libraries/XP3312.pretty/XP3312_FlyingLead.kicad_mod` |
| Mapping PCB | `hardware/pmt-interface/pmt-interface.kicad_pcb` |
| Schematic | `hardware/pmt-interface/pmt-interface.kicad_sch` |

```bash
python3 hardware/pmt-interface/gen_fp.py
python3 hardware/pmt-interface/gen_sch.py
```

Open the PCB to verify physical pad order against the tube retainer, then use the same numbers on the circular schematic symbol.
