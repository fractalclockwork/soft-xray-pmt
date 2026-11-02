# Stages 5–6 — Anode scope lane

Scope/capture lane **before** Pico integration (cinemate capture-only before HID).
**HV hold:** ≤ Stage 4 ceiling (**1000 V** first pass). Ceilings: [`ceilings.md`](ceilings.md).

---

## Stage 5 — Anode dark metrology

**Prior:** Stage 4 PASS. **Light:** dark (no LED). **Pico ADC:** no.

### Goal

Trust the anode measurement path with the tube biased and dark.

### Procedure

1. Hold HV at chosen dark bias (typically **1000 V** or last PASS hold).
2. Scope on J5: 1 MΩ input; DC-coupled via JMP_DC unless characterizing AC path.
3. Record baseline, noise floor, any dark pulses.
4. Confirm PSU current still within abort factor of prediction (measurement path not loading bias badly).
5. Optional: try AC-coupling pad (remove JMP_DC, fit C4) and compare; restore DC default after.
6. Save scope screenshot / note path under `docs/bringup/evidence/` (optional).

### Evidence

| Field | Value |
|---|---|
| HV hold (V) | |
| I_meas | |
| Coupling (DC/AC) | |
| Baseline / noise | |
| Scope evidence path | |
| Result | PASS / FAIL |

### Exit Stage 5

- [ ] Anode path characterized in dark
- [ ] No saturation / rail / excess I
- [ ] Still **no intentional photons**

**Next:** Stage 6 below. Optional Stage 4b (1200 V) may open after this PASS.

---

## Stage 6 — Pinhole LED on scope

**Prior:** Stage 5 PASS. **Stimulus:** enclosed LED + **pinhole only**.
**Pico ADC:** still no — scope must see pulses first.

### LED ceilings (until this stage PASSes)

| Key | Cap |
|---|---|
| Forward current | ≤ **5 mA** |
| Duty | ≤ **5%** |
| Preferred first HV | **800 V** (then 1000 V if needed) |
| Enclosure | pinhole required; no bare LED at photocathode |

### Procedure

1. Re-confirm blackout except pinhole path; Gate C style assent for “controlled light only.”
2. Start at **800 V** (or lower) dark baseline on scope.
3. Enable LED at minimum current / minimum duty through pinhole.
4. Confirm anode pulses on **scope**. Record amplitude / rough width / rate.
5. If needed, step LED or HV carefully — never exceed Stage 4 cap or LED ceilings.
6. Abort if anode rails, continuous anode current approaches **0.2 mA**, light leak, or I_string abort.
7. Record LED recipe (current, PWM, aperture, distance).

### Evidence

| Field | Value |
|---|---|
| HV (V) | |
| LED current / duty / aperture | |
| Pulse amplitude / duration (scope) | |
| I_string / I_anode notes | |
| Result | PASS / FAIL |

### Exit Stage 6

- [ ] Controlled optical response on scope
- [ ] LED recipe recorded
- [ ] No saturation damage indicators

**Next:** [stages-7-8-pico.md](stages-7-8-pico.md)
