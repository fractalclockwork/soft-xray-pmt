# Bring-up ceilings (fail-closed)

Hard voltage, current, and optical limits for XP3312/SQ HV bring-up.
**Do not raise these limits to pass a stage.** Encode changes only by explicit
project decision after a prior stage has already PASSed under the old ceiling.

Machine-readable keys below are the policy source; prose restates them.

## High voltage

| Key | Value | Notes |
|---|---|---|
| `hv_abs_max_v` | **1500** | Datasheet absolute maximum supply |
| `hv_first_pass_max_v` | **1000** | Stage 4 exit; do not open 1200 until Stage 5 PASS |
| `hv_optional_max_v` | **1200** | Stage 4b only, after Stage 5 PASS |
| `hv_stage_caps_v` | `[100, 400, 800, 1000, 1200]` | Per-stage hard caps (see stage docs) |
| `hv_polarity` | `negative_cathode` | −HV on K; anode near GND |

### Stage setpoints (dark ramp)

| Stage | Allowed setpoints (V, magnitude) | Cap |
|---|---|---|
| 1 Smoke | `0 → 100` hold ≥30 s | **100** |
| 2 Low dark | `250`, then `400` | **400** |
| 3 Approach | `600`, then `800` | **800** |
| 4 Nominal | `1000` | **1000** |
| 4b Optional | `1200` | **1200** (after Stage 5) |

Inter-electrode datasheet limits (Type A at ≤1200 V stays in family for
consecutive dynodes and A–D8). Early stages intentionally run **below** the
~880 V region where D1–K and A–D8 recommended minima are met — dark only.

## Supply

HV comes from an **external variable, regulated** PSU. Operator sets |V| (setpoint
authoritative). Load current is **readback**, not a programmed I setpoint.
`psu_current_limit_uA` is a **trip ceiling**, not the operating point.

## Current

| Key | Value | Notes |
|---|---|---|
| `r_string_total_ohm` | `24.2e6` | Type A string; **primary bleeder** K→GND |
| `i_string_predicted_A` | `\|V\| / 24.2e6` | Stage contract: ~4 µA @ 100 V; ~41 µA @ 1000 V |
| `i_string_abort_factor` | **3** | Abort if PSU I > 3× `i_string` |
| `psu_current_limit_uA` | **200–500** | Trip ceiling for Stage 1–4 (not operating I) |
| `i_anode_cont_max_mA` | **0.2** | Datasheet continuous anode current |
| `r_bleed_ohm` | `≥22e6` soft | Optional parallel; string already bleeds; **2×+ OK** |

**Bleed policy:** Extra `Rbleed` is non-critical. Do not require exact 22 MΩ for
stage PASS. Soft bleed may bump PSU I slightly above `i_string` (negligible if
bleed ≫ string). Still abort on **3× i_string**. Gate 0c SPICE may show higher
I(Vhv) when a placeholder bleed is on the sch — that is **not** the Stage 1–4
prediction contract.

## Optical / LED (Stages 6+)

| Key | Value | Notes |
|---|---|---|
| `led_enclosure` | `pinhole_required` | No bare LED toward photocathode |
| `led_max_forward_mA` | **5** | First-light ceiling; raise only after Stage 6 PASS |
| `led_max_duty` | **0.05** | 5% PWM / pulse duty until Stage 6 PASS |
| `led_first_hv_v` | **800** | Prefer reduced HV for first photons |
| `dark_required_before_hv` | `true` | Gate C; photocathode covered / blackout |

## Pico / isolation (Stages 7–8)

| Key | Value | Notes |
|---|---|---|
| `pico_usb_while_hv` | **forbidden** | Battery or isolated 3V3 only when HV live |
| `hv_sense_adc_max_v` | **3.3** | Clamp mandatory on sense divider output |
| `ota_hv_v` | **0** | OTA / WiFi offload with HV off and cathode covered |
| `anode_to_pico_adc` | `conditioned_only` | Peak-hold / stretcher / comparator — not raw ns pulses |

## Operator rules

1. Refuse a stage if the prior gate/stage is not **PASS**.
2. Human confirm dark-safe (Gate C) before every energize session.
3. On abort: set PSU to 0 V, wait for bleed, then re-open Gate B/C as needed.
4. Never probe dynode taps with a normal DMM under HV.
5. Scope anode lane (Stages 5–6) must PASS before Pico anode integration (Stage 7).
