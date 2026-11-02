# Gate 0b — Operator schematic verification (page 2)

**Energize:** No. **Prior:** auto-validate PASS on bringup-supply (label-routed, **no shorts**).

Hard gate **before** Gate 0c SPICE. Page-2 keeps **segment equivalents**
(`R10=4.4M` … `R18=1.1M`) permanently for sim / validate / test; Gate A stuffing
uses **STUFF:** annotations + [`bom-divider.md`](bom-divider.md) — **no R10A sch redraw**.
Rev `0.5-stuff-annot`.

## Auto checks

```bash
python3 hardware/pmt-interface/gen_bringup_sch.py --validate
python3 hardware/pmt-interface/gen_sch.py --validate
```

Expect `BRINGUP VALIDATE OK`. Generator **forbids** R10A/R18A schematic symbols.

## Operator checklist (KiCad)

| # | Check | Pass |
|---|---|---|
| 1 | Distinct nets **D1…D8**, **K**, **GND**, **A** | [x] |
| 2 | J4 map: .7=K, .8=D1, .9=D2, .6=D3, .5=D4, .4=D5, .12=D6, .3=D7, .2=D8, .14=GND | [x] |
| 3 | J4.8 ≠ J4.9 | [x] |
| 4 | String bodies are equivalents R10–R18; STUFF notes only (no R10A/R18A symbols) | [x] |
| 5 | Mate uses **labels**, not a shared stub bus | [x] |
| 6 | Auto-validate PASS | [x] |

## Sign-off

| Field | Value |
|---|---|
| Date | 2026-11-02 |
| Operator | operator |
| Result | **PASS** |

**Next:** [`gate-0-spice.md`](gate-0-spice.md) (PASS) → [`gate-a-build.md`](gate-a-build.md)
(stuff 2.2M/3.3M per [`bom-divider.md`](bom-divider.md); sch stays equivalents).
