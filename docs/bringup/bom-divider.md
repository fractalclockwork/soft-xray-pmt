# Bring-up BOM — Type A divider + anode measurement

Canonical parts list for page-2 harness/card mating to the verified Philips filter
board. Schematic:
[`bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch)
(rev `0.5-stuff-annot`).

| | |
|---|---|
| Design lock | Type A, unit **2.2 MΩ**, total **24.2 MΩ** |
| **Schematic** | **Segment equivalents only** — R10=4.4M … R18=1.1M (sim / validate / test) |
| **Stuffing** | Sourced **2.2 MΩ** + **3.3 MΩ** networks per table below — **not** redrawn as R10A… |
| Policy | Equiv bodies stay on sch to reduce sim, validation, and test errors |
| Polarity | **−HV → K**; anode not in divider end |
| Mate | J4 → J1 wrap; nets via **labels** |
| Gates | 0b+0c **PASS** → [`gate-a-build.md`](gate-a-build.md) |

---

## Suggested 2.2 MΩ / 3.3 MΩ combinations (documentation artifact)

Sch keeps one body per segment. At Gate A, **stuff** the sourced network that
equals that segment. Silk/annotations on page-2 echo the same map.

| Segment | Ratio | Sch body (equiv) | Stuff network (sourced SKUs) |
|---|---|---|---|
| K–D1 | 2 | **R10 = 4.4 MΩ** | **R10A + R10B** = 2× **2.2 MΩ** series |
| D1–D2 | 1.5 | **R11 = 3.3 MΩ** | 1× **3.3 MΩ** |
| D2–D3 | 1.5 | **R12 = 3.3 MΩ** | 1× **3.3 MΩ** |
| D3–D4 | 1.5 | **R13 = 3.3 MΩ** | 1× **3.3 MΩ** |
| D4–D5 | 1 | **R14 = 2.2 MΩ** | 1× **2.2 MΩ** |
| D5–D6 | 1 | **R15 = 2.2 MΩ** | 1× **2.2 MΩ** |
| D6–D7 | 1 | **R16 = 2.2 MΩ** | 1× **2.2 MΩ** |
| D7–D8 | 1 | **R17 = 2.2 MΩ** | 1× **2.2 MΩ** |
| D8–GND | 0.5 | **R18 = 1.1 MΩ** | **R18A ∥ R18B** = 2× **2.2 MΩ** parallel |
| **Σ** | 11 | **24.2 MΩ** | same |

Do **not** add R10A/R18A as schematic symbols — generator refuses them by policy.

---

## Shopping (Gate A)

| SKU | Qty (min) | Use |
|---|---|---|
| **2.2 MΩ** ½ W ±1% | **8** + spares | series for R10, singles R14–R17, parallel for R18 |
| **3.3 MΩ** ½ W ±1% | **3** + spares | R11–R13 |
| **≥22 MΩ** HV (22 M fine; **2×+ OK**) | 1 | Rbleed soft parallel (optional exact value) |
| **47 Ω** | 1 | R19 |

---

## Master line items (Gate A populate)

| Sch ref | Stuff as | Value / network | Qty bodies | Populate |
|---|---|---|---|---|
| R10 | R10A+R10B series | 2× 2.2M | 2 | Gate A |
| R11–R13 | same refs | 3.3M each | 3 | Gate A |
| R14–R17 | same refs | 2.2M each | 4 | Gate A |
| R18 | R18A∥R18B | 2× 2.2M parallel | 2 | Gate A |
| Rbleed | Rbleed | ≥22M soft | 1 | Gate A (string already bleeds) |
| R19 | R19 | 47R | 1 | Gate A |
| J3, J4, J5, JMP_DC | — | — | 1 ea | Gate A |
| C4, R20, R21, C5 | — | — | — | DNP / later |
| Vhv, Iph, Ra, Ca | — | sim-only | — | never stuff |

---

## J4 pin map

| J4 | Net | J4 | Net |
|---|---|---|---|
| 2 | D8 | 8 | D1 |
| 3 | D7 | 9 | D2 |
| 4 | D5 | 12 | D6 |
| 5 | D4 | 13 | NC |
| 6 | D3 | 14 | GND |
| 7 | K (−HV) | 1, 10, 11 | NC |

---

## Predicted current

**Stage contract (string):** `I ≈ |V| / 24.2e6` (~41 µA @ 1000 V); abort at 3×.
HV from external **variable regulated** PSU — I is load readback.

Soft `Rbleed` (≥22 M) is non-critical; may bump PSU I slightly. Sch/sim may show
a placeholder 22 M and higher I(Vhv) — that is **not** the Stage 1–4 contract.
See [`ceilings.md`](ceilings.md).
