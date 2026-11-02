# Gate C — Optical dark-safe

**Energize:** No until Stage 1 ramp starts. **Prior:** Gate B PASS.
Analogue to spectrometer-lab forcing shutter OFF before stimulus.

## Goal

Prove the tube cannot see ambient or test light before first HV. Operator assent
required (cinemate / rad-lab style).

## Checklist

| # | Check | Pass |
|---|---|---|
| 1 | Tube inside light shield / blackout enclosure | [ ] |
| 2 | Photocathode covered **or** enclosure proven dark (no visible leak) | [ ] |
| 3 | Test LED unpowered; driver disconnected or disabled | [ ] |
| 4 | Pico unpowered or USB/battery removed for Stages 1–5 | [ ] |
| 5 | Scope on anode BNC J5; **1 MΩ** input (default); baseline known | [ ] |
| 6 | Variable regulated HV PSU: voltage **0 V**, output enabled only when ready; current-limit **trip** **200–500 µA** per [`ceilings.md`](ceilings.md) | [ ] |
| 7 | Emergency off / kill path known | [ ] |
| 8 | Bleed path present on bring-up board | [ ] |
| 9 | Operator assent: “dark confirmed, ready for Stage 1” | [ ] |

Operator / date: _______________

## Exit Gate C

- [ ] All rows PASS
- [ ] Still **0 V** on tube until Stage 1 deliberately ramps

**Next:** [stage-1-smoke.md](stage-1-smoke.md)

On any later session restart after opening the enclosure: **re-run Gate C** before
energizing again.
