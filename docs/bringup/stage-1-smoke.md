# Stage 1 — HV smoke (100 V)

**Prior:** Gate C PASS. **Ceiling:** **100 V** ([`ceilings.md`](ceilings.md)).
**Light:** dark only. **Pico:** no.

## Goal

First energization at minimal voltage on the external **variable regulated** PSU.
Confirm load current ≈ string prediction and no arcing before climbing the ramp.

## Predicted

| \|Vs\| | I_pred (string) | Abort if I > |
|---|---|---|
| 100 V | ~4.1 µA | ~12 µA (3×) |

Soft parallel bleed may bump PSU I slightly above I_pred — still abort only at 3×.
Current-limit 200–500 µA is a trip ceiling, not the operating point.

## Procedure

1. Re-confirm Gate C dark-safe.
2. Mate bring-up J4 to tube J1; anode scope on J5.
3. PSU: current-limit trip **200–500 µA**; voltage 0 V; polarity −HV → K.
4. Enable output at 0 V; verify I ≈ 0.
5. Ramp slowly **0 → 100 V**. Hold ≥ **30 s**.
6. Record PSU voltage setpoint, measured I (load readback), anode scope note.
7. Abort immediately on arc, smell, excess current, loss of regulation, or anomalous anode DC.
8. On abort: PSU → 0 V; wait for string bleed-down; reopen Gate B/C as needed.

## Evidence log

| Field | Value |
|---|---|
| Date / operator | |
| PSU setpoint (V) | |
| Measured I | |
| Anode scope note | |
| Result | PASS / FAIL |

## Exit Stage 1

- [ ] Hold at 100 V ≥30 s with I within abort factor of prediction
- [ ] No arc / smell / runaway
- [ ] Evidence recorded

**Next:** [stages-2-4-hv-ramp.md](stages-2-4-hv-ramp.md#stage-2--low-bias-dark)
