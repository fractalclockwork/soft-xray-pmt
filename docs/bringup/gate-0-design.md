# Gate 0 — Design / schematic / BOM

**Energize:** No (0 V). **Prior:** continuity map PASS.

## Goal

Lock the bring-up electrical design before any build: hierarchical schematic
page 2, divider BOM, and [`ceilings.md`](ceilings.md).

## Deliverables checklist

| Item | Path | Done |
|---|---|---|
| Ceilings policy | [`ceilings.md`](ceilings.md) | [x] |
| Bring-up index | [`README.md`](README.md) | [x] |
| KiCad page 2 | [`../../hardware/pmt-interface/bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch) | [x] |
| Generator | [`../../hardware/pmt-interface/gen_bringup_sch.py`](../../hardware/pmt-interface/gen_bringup_sch.py) | [x] |
| Divider BOM (2.2M/3.3M) | [`bom-divider.md`](bom-divider.md) | [x] |
| Operator sch verify | [`gate-0-sch-verify.md`](gate-0-sch-verify.md) | [x] PASS |
| SPICE gate (KiCad) | [`gate-0-spice.md`](gate-0-spice.md) | [x] PASS |
| 2.2M/3.3M stuffing map | [`bom-divider.md`](bom-divider.md) + sch STUFF notes | [x] annotate-only |
| Root README links | [`../../README.md`](../../README.md) | [x] |

## Page 2 blocks (required)

1. **HV in** — external **variable regulated** PSU (−HV, GND), polarity note, soft bleed (≥22 M), current-limit trip note.
2. **Type A divider** — ratios `2 : 1.5 : 1.5 : 1.5 : 1 : 1 : 1 : 1 : 0.5`, unit 2.2 MΩ; TP at each dynode; bring-up **J4** mates tube **J1** (same wrap numbers).
3. **Anode measurement** — BNC/scope takeoff from A/GND; optional AC-coupling pads; stock **R2** stays on tube board (page 1).
4. **HV sense** (Stage 7+, may be DNP) — separate high-ratio string + 3.3 V clamp.
5. **Pico stubs** (Stage 7–8) — LED driver note; anode front-end stub; isolated/battery 3V3; no USB while HV live.

## Type A string (design lock)

Bring-up plug **J4** ↔ tube socket **J1** (identical wrap pin numbers below).

| Segment | Ratio | R | J4 / J1 |
|---|---|---|---|
| K–D1 (−HV at K) | 2 | 4.4 MΩ (sch R10; stuff 2×2.2M series) | .7 = K; .8 = D1 |
| D1 → D2 | 1.5 | 3.3 MΩ (R11) | .9 |
| D2 → D3 | 1.5 | 3.3 MΩ (R12) | .6 |
| D3 → D4 | 1.5 | 3.3 MΩ (R13) | .5 |
| D4 → D5 | 1 | 2.2 MΩ (R14) | .4 |
| D5 → D6 | 1 | 2.2 MΩ (R15) | .12 |
| D6 → D7 | 1 | 2.2 MΩ (R16) | .3 |
| D7 → D8 | 1 | 2.2 MΩ (R17) | .2 |
| D8 → GND | 0.5 | 1.1 MΩ (sch R18; stuff 2×2.2M ∥) | .14 |

Anode **not** in the divider end — coax / measurement path only. Pin **.13** filter AC only; **.1/.10/.11** NC.

## Regenerate schematic

```bash
python3 hardware/pmt-interface/gen_bringup_sch.py
python3 hardware/pmt-interface/gen_sch.py   # root sheet + hierarchical link
```

## Exit Gate 0

- [x] `ceilings.md` committed with stage caps
- [x] Page 2 schematic present; divider + anode path drawn; stubs labeled
- [x] [`bom-divider.md`](bom-divider.md) lists HV-rated parts / series strings
- [x] No parts energized

**Next:** [gate-a-build.md](gate-a-build.md) (0b+0c PASS; stuff per bom-divider, no sch redraw)
