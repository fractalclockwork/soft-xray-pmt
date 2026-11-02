# Pin reconciliation — XP3312/SQ + filter board

**Status: stage-1 continuity verified (2026-11-01).**  
Authoritative record of unpowered DMM checks. Supersedes README pencil notes and earlier “probable” bypass guesses.

## Counting convention (locked)

View = **from the bottom of the tube looking up** (pins facing you). Short pin **`sp`** at south. Numbered pins **1…19 clockwise**.

Confirmed by continuity: **D1 (pin 1) → J1.8** and **K (pin 16) → R1 → J1.7** only line up with that bottom-up / CW datasheet view.

Opposite (CCW) counting lands the same physical cathode on label **“4”** — old dual pencil/pen map (`4/16/K`). Use datasheet / CW numbers only.

Board-side cathode landmark: blue **`472Z` 2 kV** (C1) + **`1001` 1 kΩ** (R1).

## J1 socket numbering (locked)

**Wide IC / DIP-14 style 2×7 socket** — **7.62 mm (300 mil) row spacing**, wrap pin order.  
**Not** an IDC ribbon dual-row (2.54 mm row pitch, Odd/Even numbering).

Same wrap convention as Prutchi XP2422 Fig. 3 / DIP-14:

```text
  1 ──┤ ├─ 14
  2 ──┤ ├─ 13
  3 ──┤ ├─ 12
  4 ──┤ ├─ 11
  5 ──┤ ├─ 10
  6 ──┤ ├─  9
  7 ──┤ ├─  8
```

(Equivalent horizontal view: bottom `1–7` L→R, top `8–14` R→L.)

KiCad footprint: `XP3312:HDR_2x7_IC_Socket` (body ≈ DIP-14 socket, pads at ±3.81 mm).  
Electrode **assignments** differ from the XP2422 figure; only the **1–14 wrap geometry** matches.

## Tube electrodes

| Electrode | Datasheet pin | Continuity |
|---|---|---|
| D1 | 1 | yes → J1.8 |
| D2 | 3 | yes → J1.9 |
| D3 | 4 | yes → J1.6 |
| D4 | 7 | yes → J1.5 |
| D5 | 8 | yes → J1.4 |
| D6 | 9 | yes → J1.12 |
| D7 | 10 | yes → J1.3 (hardwire only; not in R/C cluster) |
| D8 | 11 | yes → J1.2 (+ bypass cap to mid) |
| A | 12 | yes → coax center; ~1 MΩ to GND |
| K | 16 | yes — C1 to GND; R1 → J1.7 |
| sp | key | orientation reference |
| ic | 2,5,6,13–15,17–19 | not exercised today |

## Tube → J1 (verified)

| Electrode | J1 | Passive | OK? |
|---|---|---|---|
| D8 | 2 | + C3 to bypass mid | yes |
| D7 | 3 | — | yes |
| D5 | 4 | — | yes |
| D4 | 5 | — | yes |
| D3 | 6 | — | yes |
| K | 7 | R1 1k; C1 to GND | yes |
| D1 | 8 | — | yes |
| D2 | 9 | — | yes |
| D6 | 12 | — | yes |
| filter (AC) | 13 | C2 to bypass mid | yes |
| GND | 14 | coax shell | yes |
| A | coax center | R2 ~1 MΩ to GND | yes |
| NC? | 1, 10, 11 | photo-consistent open; DMM still required (11 least clear) | |

## Bypass / anode cluster (verified)

```text
   D8 (11) / J1.2 ---- C3 (tan MLCC) ----+
                                         +----- R3 10Ω (`100`) ----- GND / J1.14
   J1.13 ---------------- C2 (tan MLCC) -+
```

| Check | Result |
|---|---|
| A ↔ coax center | ~0 Ω |
| A → GND | ~1 MΩ (marking `115` / 1.1 MΩ) |
| K → J1.7 | via R1 1 kΩ |
| R3 one side → GND | confirmed |
| One MLCC → D8 ↔ mid (R3) | confirmed |
| Other MLCC → J1.13 ↔ mid (R3) | confirmed (**not** D7) |

Earlier photo/ANALOG guess put the second cap on **D7**. Continuity shows that cap on **J1.13** instead; D7 remains a straight breakout to J1.3.
