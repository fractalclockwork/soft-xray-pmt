# HV power and sense bring-up

Ordered guides for biasing the XP3312/SQ through the verified Philips filter/breakout
board. **Refuse later stages until the prior gate/stage is PASS.** Do not raise
[`ceilings.md`](ceilings.md) limits to pass a stage.

Prior work (complete — not an HV stage): tube↔J1 continuity map —
[`../continuity-checklist.md`](../continuity-checklist.md),
[`../probable-netlist.md`](../probable-netlist.md). **No HV applied yet.**

## Status

| ID | Guide | Energize | Cap | Status |
|---|---|---|---|---|
| Prior | Continuity map | No | 0 V | **PASS** (2026-11-01) |
| Gate 0 | [gate-0-design.md](gate-0-design.md) | No | 0 V | **PASS** — ceilings + equiv sch + BOM policy |
| Gate 0b | [gate-0-sch-verify.md](gate-0-sch-verify.md) | No | 0 V | **PASS** — operator |
| Gate 0c | [gate-0-spice.md](gate-0-spice.md) | No | 0 V | **PASS** — mech + operator KiCad |
| Gate A | [gate-a-build.md](gate-a-build.md) | No | 0 V | **Open (on hold)** — stuff 2.2M/3.3M per BOM annot |
| Gate B | [gate-b-cold.md](gate-b-cold.md) | No | 0 V | Open |
| Gate C | [gate-c-dark.md](gate-c-dark.md) | No | 0 V | Open |
| Stage 1 | [stage-1-smoke.md](stage-1-smoke.md) | Yes | **100 V** | Open |
| Stage 2 | [stages-2-4-hv-ramp.md](stages-2-4-hv-ramp.md#stage-2--low-bias-dark) | Yes | **400 V** | Open |
| Stage 3 | [stages-2-4-hv-ramp.md](stages-2-4-hv-ramp.md#stage-3--approach-rated) | Yes | **800 V** | Open |
| Stage 4 | [stages-2-4-hv-ramp.md](stages-2-4-hv-ramp.md#stage-4--nominal-dark) | Yes | **1000 V** | Open |
| Stage 5 | [stages-5-6-anode-scope.md](stages-5-6-anode-scope.md#stage-5--anode-dark-metrology) | Yes | ≤1000 V | Open |
| Stage 6 | [stages-5-6-anode-scope.md](stages-5-6-anode-scope.md#stage-6--pinhole-led-on-scope) | Yes | ≤1000 V | Open |
| Stage 7 | [stages-7-8-pico.md](stages-7-8-pico.md#stage-7--pico-sense--led) | Yes | ≤1000 V | Open |
| Stage 8 | [stages-7-8-pico.md](stages-7-8-pico.md#stage-8--air-gap-ota--logging) | OTA @ 0 V | 0 V HV | Open |

Policy: [`ceilings.md`](ceilings.md).
**Bring-up BOM** (Gate A parts, DNP, shopping): [`bom-divider.md`](bom-divider.md).
Schematic page 2: [`../../hardware/pmt-interface/bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch).

## Ladder

```text
Prior continuity PASS
  → Gate 0 design + equiv schematic (shorts fixed)
  → Gate 0b operator sch verify
  → Gate 0c SPICE mech + **operator** KiCad verify
  → Gate A build (stuff 2.2M/3.3M per bom-divider; sch equiv + STUFF notes)
  → Gate B unpowered verify
  → Gate C optical dark-safe
  → Stage 1  100 V smoke
  → Stage 2  250 / 400 V dark
  → Stage 3  600 / 800 V dark
  → Stage 4  1000 V dark (1200 optional later)
  → Stage 5  anode dark on scope
  → Stage 6  pinhole LED on scope
  → Stage 7  Pico HV-sense + LED
  → Stage 8  air-gap OTA / onboard log
```

## Electrical summary

- HV from external **variable regulated** PSU (−HV on K); Type A string unit **2.2 MΩ**, total **24.2 MΩ** (primary bleeder).
- Soft `Rbleed` ≥22 M optional; value not critical for stage PASS.
- Bring-up **J4** mates tube-board **J1** (same wrap pin numbers; not ribbon Odd/Even).
- Anode: stock coax + page-1 **R2** ~1.1 MΩ. Page-2 sim **Ra** models that load — **never stuff** Vhv/Iph/Ra/Ca.
- Stage I contract: `I ≈ |V| / 24.2 MΩ`; abort if PSU I > 3×. Current-limit 200–500 µA is a trip ceiling.

## Sibling methodology

Same evidence culture as spectrometer-lab (Gate A pre-power), rad-lab (encoded
ceilings), cinemate-gateway (scope/capture lane before Pico integration), and
crt-drive (prove safe path before hazardous load).
