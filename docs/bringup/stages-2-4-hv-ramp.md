# Stages 2–4 — Dark HV ramp

**Prior:** Stage 1 PASS. **Light:** dark only. **Pico:** no.
Ceilings: [`ceilings.md`](ceilings.md). Never probe dynodes with a normal DMM under HV.

Shared rules for every setpoint (external **variable regulated** PSU):

1. Prior stage PASS required; re-confirm Gate C dark before the session.
2. Set |V|; watch load I vs string `I ≈ |V| / 24.2 MΩ`; abort if I > 3× predicted.
3. Soft bleed may bump I slightly above I_pred — abort still at 3× string, not an exact bleed model.
4. Abort on arc, smell, enclosure breach, runaway anode, or loss of regulation.
5. On abort: 0 V → string bleed-down → Gate B/C as needed. Do **not** raise ceilings to pass.
6. Record V setpoint, I readback, anode note for each hold.

| \|Vs\| | I_pred (string) | Abort I (3×) |
|---|---|---|
| 250 V | ~10 µA | ~31 µA |
| 400 V | ~17 µA | ~50 µA |
| 600 V | ~25 µA | ~74 µA |
| 800 V | ~33 µA | ~99 µA |
| 1000 V | ~41 µA | ~124 µA |
| 1200 V | ~50 µA | ~149 µA |

---

## Stage 2 — Low bias dark

**Ceiling:** **400 V**.

| Step | Setpoint | Hold | Pass |
|---|---|---|---|
| 2a | **250 V** | ≥30 s | [ ] |
| 2b | **400 V** | ≥30 s | [ ] |

### Evidence

| Setpoint | I_meas | Anode note | Pass |
|---|---|---|---|
| 250 V | | | [ ] |
| 400 V | | | [ ] |

**Exit Stage 2:** both holds PASS; anode near baseline in dark.

---

## Stage 3 — Approach rated

**Ceiling:** **800 V**. Enters datasheet supply minimum at 800 V.

| Step | Setpoint | Hold | Pass |
|---|---|---|---|
| 3a | **600 V** | ≥30 s | [ ] |
| 3b | **800 V** | ≥30 s | [ ] |

### Evidence

| Setpoint | I_meas | Anode note | Pass |
|---|---|---|---|
| 600 V | | | [ ] |
| 800 V | | | [ ] |

**Exit Stage 3:** both holds PASS; still dark.

---

## Stage 4 — Nominal dark

**Ceiling (first pass):** **1000 V**. Do not exceed 1000 V until Stage 5 PASS
opens optional Stage 4b.

| Step | Setpoint | Hold | Pass |
|---|---|---|---|
| 4a | **1000 V** | ≥60 s | [ ] |

### Evidence

| Setpoint | I_meas | Anode note | Pass |
|---|---|---|---|
| 1000 V | | | [ ] |

**Exit Stage 4:** 1000 V dark hold PASS. **Stop here** for first-pass HV.

**Next:** [stages-5-6-anode-scope.md](stages-5-6-anode-scope.md#stage-5--anode-dark-metrology)

---

## Stage 4b — Optional 1200 V (later)

**Prior:** Stage 4 PASS **and** Stage 5 PASS. **Ceiling:** **1200 V**.
Never exceed `hv_abs_max_v` 1500 V.

| Step | Setpoint | Hold | Pass |
|---|---|---|---|
| 4b | **1200 V** | ≥60 s | [ ] |

Not required for Stages 6–8 first pass; keep first-pass hold at 1000 V unless
characterization needs 1200.
