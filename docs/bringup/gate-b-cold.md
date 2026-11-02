# Gate B — Unpowered verify

**Energize:** No. PSU disconnected or locked output-off at 0 V.
**Prior:** Gate A PASS.

## Goal

First measurement of the **stuffed** 2.2 MΩ / 3.3 MΩ networks and mate pin map
before first HV. Gate A assembles; Gate B proves segment resistances, polarity,
and anode path.

Reference map: [`../probable-netlist.md`](../probable-netlist.md). Stuffing artifact:
[`bom-divider.md`](bom-divider.md). Sch keeps equiv R10–R18; **R10A/B, R18A/B are
physical stuffing labels only** (not schematic symbols).

## Segment resistance checklist

Measure across each **segment** (not every body unless debugging).

In-circuit caveat: with the full string joined, a DMM across one segment can read
low via the rest of the chain — lift one end of the segment under test if a face
value fails unexpectedly.

| # | Segment | Physical stuff | Expected | Measured | Pass |
|---|---|---|---|---|---|
| 1 | K–D1 | R10A+R10B series (sch R10) | **4.4 MΩ** ±tol | | [ ] |
| 2 | D1–D2 | R11 | **3.3 MΩ** | | [ ] |
| 3 | D2–D3 | R12 | **3.3 MΩ** | | [ ] |
| 4 | D3–D4 | R13 | **3.3 MΩ** | | [ ] |
| 5 | D4–D5 | R14 | **2.2 MΩ** | | [ ] |
| 6 | D5–D6 | R15 | **2.2 MΩ** | | [ ] |
| 7 | D6–D7 | R16 | **2.2 MΩ** | | [ ] |
| 8 | D7–D8 | R17 | **2.2 MΩ** | | [ ] |
| 9 | D8–GND | R18A∥R18B (sch R18) | **1.1 MΩ** | | [ ] |
| 10 | −HV → GND | Type A **string** | ≈ **24.2 MΩ** | | [ ] |

Row 10 is the **string** design check. Soft `Rbleed` (≥22 M, value non-critical)
parallels the string: lift one end of bleed before row 10, **or** record the
parallel reading with a note (if bleed ≫ string, reading still ~24 M — not a hard fail).

### Optional per-body

| # | Check | Expected | Pass |
|---|---|---|---|
| O-body | Each of R10A/B, R14–R17, R18A/B | ≈ 2.2 MΩ | [ ] |
| O-body | R11, R12, R13 | ≈ 3.3 MΩ | [ ] |

## Mate / polarity / anode

Bring-up plug **J4** mates tube-board **J1** (same wrap numbers).

| # | Check | Expected | Pass |
|---|---|---|---|
| 11 | J4.7 ↔ K / −HV node | ~0 Ω | [ ] |
| 12 | J4.8 ↔ D1 | ~0 Ω | [ ] |
| 13 | J4.9 ↔ D2 | ~0 Ω | [ ] |
| 14 | J4.6 ↔ D3 | ~0 Ω | [ ] |
| 15 | J4.5 ↔ D4 | ~0 Ω | [ ] |
| 16 | J4.4 ↔ D5 | ~0 Ω | [ ] |
| 17 | J4.12 ↔ D6 | ~0 Ω | [ ] |
| 18 | J4.3 ↔ D7 | ~0 Ω | [ ] |
| 19 | J4.2 ↔ D8 | ~0 Ω | [ ] |
| 20 | J4.14 ↔ GND | ~0 Ω | [ ] |
| 21 | J4.13 not tied to −HV or string | open / filter-only | [ ] |
| 22 | Polarity silk: −HV feeds K path | confirmed | [ ] |
| 23 | With tube mated: A ↔ coax center | ~0 Ω | [ ] |
| 24 | A → GND via stock R2 (page 1) | ≈ 1.0–1.2 MΩ | [ ] |
| 25 | J5 center ↔ A path; shell ↔ GND | continuous | [ ] |
| 26 | LED/Pico disconnected for Stages 1–5 | confirmed | [ ] |
| 27 | Sim-only Vhv/Iph/Ra/Ca not stuffed | confirmed | [ ] |

## Abort

**Refuse Stage 1** if any required row fails.

## Exit Gate B

- [ ] Required rows PASS
- [ ] Date / operator: _______________
- [ ] Still **0 V**

**Next:** [gate-c-dark.md](gate-c-dark.md)
