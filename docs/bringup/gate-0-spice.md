# Gate 0c — SPICE verification (KiCad page-2)

**Energize:** No. **Prior:** Gate 0b operator schematic verify PASS
([`gate-0-sch-verify.md`](gate-0-sch-verify.md)).

Hard gate **before** Gate A stuffing. Schematic stays on segment equivalents;
2.2 MΩ / 3.3 MΩ combinations are a **documentation / annotation** artifact only
([`bom-divider.md`](bom-divider.md)) — not an R10A redraw.

**Gate 0c cannot PASS without operator verification of the KiCad result.**
A green `run_bringup_sims.sh` exit is **mech prep only** — not gate closure.

## Source of truth

| Item | Path |
|---|---|
| Schematic | [`bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch) |
| Export | `kicad-cli sch export netlist --format spice` |
| Mech runner | [`../../sim/spice/run_bringup_sims.sh`](../../sim/spice/run_bringup_sims.sh) |
| Last export | [`../../sim/spice/kicad-out/bringup-supply.cir`](../../sim/spice/kicad-out/bringup-supply.cir) |

Hand decks `type_a_divider.cir` / `anode_pulse.cir` are reference only.

## What is on the sheet (sim)

| Ref | Role |
|---|---|
| Vhv | VDC −1000 V on **K** (sim-only) |
| R10–R18, Rbleed | Type A string + bleed (hardware equiv bodies) |
| Ra, Ca | Anode load 1.1 MΩ + 15 pF (sim-only) |
| Iph | Photon-like pulse ≈ 36 pC / 10 ns into A (sim-only) |
| J3/J4/J5/JMP/DNP | `exclude_from_sim` |

PMT model is **intentionally simplified** (resistive bias + pulsed anode current).

## Mech prep (agent or operator)

```bash
bash sim/spice/run_bringup_sims.sh
```

Expect exit 0 and `SPICE MECH OK` (not gate PASS).

---

## Operator procedure — KiCad Simulator

Open `hardware/pmt-interface/bringup-supply.kicad_sch` in the schematic editor
(`eeschema` or KiCad project → page 2).

### 0. Open the simulator

1. **Inspect → Simulator** (or the simulator toolbar icon).
2. Confirm sim sources: **Vhv** (left of HV), and near anode **Iph**, **Ra**, **Ca**.
3. Connectors J3/J4/J5 excluded from sim — expected.

### 1. Voltage probes — divider (DC / OP)

**Analysis:** Operating Point (DC).

Probe these **global** nets (voltage probe on the label):

| Probe | Expect @ Vhv = −1000 V |
|---|---|
| **K** | −1000 V |
| **D1** | ≈ −818.2 V |
| **D2** | ≈ −681.8 V |
| **D3** | ≈ −545.5 V |
| **D4** | ≈ −409.1 V |
| **D5** | ≈ −318.2 V |
| **D6** | ≈ −227.3 V |
| **D7** | ≈ −136.4 V |
| **D8** | ≈ −45.5 V |
| **A** (idle) | ≈ 0 V |

Optional: current through **Vhv** ≈ **87 µA** (string ~41 µA + bleed ~45 µA).

**Step 1 PASS:** D1 and D8 within ~2% of table; voltages step monotonically toward GND down the string.

### 2. Stimulus — photon current pulse

**Iph** (sim-only): `PULSE(0 3.6m 50n 0.5n 0.5n 10n 1)`

| Param | Meaning |
|---|---|
| 0 → 3.6 mA | Peak conventional current **A → GND** (electrons into anode) |
| td = 50 ns | Pulse starts |
| tw = 10 ns | Width → charge ≈ 36 pC |
| per = 1 s | Single pulse in a short TRAN window |

**Analysis:** Transient, e.g. `0` → `200n`, step `~0.2n`.

Optional: probe **I(Iph)** — expect 3.6 mA pulse near 50–60 ns.

### 3. Anode response to stimulus

Keep TRAN. Probe **V(A)** (optional: current through **Ra**).

| What | Expect |
|---|---|
| Before ~50 ns | V(A) ≈ 0 |
| During/after pulse | V(A) goes **negative** |
| Min in ~40–120 ns | **A_MIN ≈ −2.5 V** (with Ca = 15 pF) |
| Shape | Brief negative spike, then recover toward 0 |

**Step 3 PASS:** anode clearly negative; amplitude volts-scale (not ~kV — that means Ca missing).

### Alternate: export review

Instead of (or in addition to) the GUI: open
[`kicad-out/bringup-supply.cir`](../../sim/spice/kicad-out/bringup-supply.cir) and the
OP/TRAN console from the mech run; confirm the same numbers.

---

## Checklist

| # | Check | Mech | Operator |
|---|---|---|---|
| 1 | Export has Vhv, Iph, Ra, R10–R18 (no `__` stubs) | [x] | [x] |
| 2 | OP probes: D1 ≈ −818.18 V, D8 ≈ −45.45 V @ −1000 V | [x] | [x] |
| 3 | OP: \|I(Vhv)\| includes placeholder bleed on sch (not Stage 1–4 I contract) | [x] | [x] |
| 4 | TRAN: anode **negative** (A_MIN ≈ −2.5 V w/ Ca) | [x] | [x] |
| 5 | Operator agrees KiCad result is acceptable | — | [x] |

## Sign-off

| Field | Value |
|---|---|
| Date | 2026-11-02 |
| Operator | operator |
| KiCad path used | Simulator + mech |
| Result | **PASS** |

## After PASS

1. Gate A: stuff per [`bom-divider.md`](bom-divider.md) + page-2 **STUFF:** annotations (equiv sch unchanged).
2. Do **not** redraw R10A/R18A on the schematic.
3. [`gate-a-build.md`](gate-a-build.md).
