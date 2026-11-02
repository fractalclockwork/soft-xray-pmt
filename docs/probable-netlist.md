# Verified netlist (stage-1 continuity)

**Supersedes** photo/ANALOG “probable” guesses. Source of truth: [`pin-reconciliation.md`](pin-reconciliation.md) (2026-11-01 DMM).  
Filename kept for existing links.

## Tube electrodes (Prutchi Fig. 4 + continuity)

Reference = short pin **`sp`**, then **clockwise**, viewed **from the bottom of the tube looking up**.

| Tube pin | Electrode | Role on stock PCB |
|---|---|---|
| 1 | D1 | → J1.8 |
| 2 | ic | leave open |
| 3 | D2 | → J1.9 |
| 4 | D3 | → J1.6 |
| 5–6 | ic | leave open |
| 7 | D4 | → J1.5 |
| 8 | D5 | → J1.4 |
| 9 | D6 | → J1.12 |
| 10 | D7 | → J1.3 (no local bypass cap) |
| 11 | D8 | → J1.2 + C3 into filter mid |
| 12 | A | → coax center + R2 to GND |
| 13–15 | ic | leave open |
| 16 | K | → C1 to GND; R1 1k → J1.7 |
| 17–19 | ic | leave open |

## J1 physical numbering

Wide IC wrap socket (Prutchi Fig. 3 convention), **not** ribbon Odd/Even:

```text
  1 ──┤ ├─ 14
  2 ──┤ ├─ 13
  3 ──┤ ├─ 12
  4 ──┤ ├─ 11
  5 ──┤ ├─ 10
  6 ──┤ ├─  9
  7 ──┤ ├─  8
```

## Circuit (stock I/O filter PCB)

```text
                    +----- C1 4.7nF/2kV ---- GND
                    |
   K (16) ----------+----- R1 1k ---------- J1.7
   D1 (1)  ------------------------------- J1.8
   D2 (3)  ------------------------------- J1.9
   D3 (4)  ------------------------------- J1.6
   D4 (7)  ------------------------------- J1.5
   D5 (8)  ------------------------------- J1.4
   D6 (9)  ------------------------------- J1.12
   D7 (10) ------------------------------- J1.3
   D8 (11) ----+-------------------------- J1.2
               |
              C3 (tan MLCC)
               |
               +----- R3 10R ----- GND / J1.14
               |
              C2 (tan MLCC)
               |
   J1.13 ------+

   A (12) -----+----- R2 ~1.1M ----------- GND
               |
               +-------------------------- J2 coax CENTER

   GND ----------------------------------- J2 SHELL, J1.14, C1, R2, R3

   J1.1, J1.10, J1.11 -------------------- NC (photo-consistent open; DMM still required, esp. 11)
```

### Correction vs earlier draft

| Element | Old guess | Verified |
|---|---|---|
| Filter caps | D7 and D8 to mid | **D8** and **J1.13** to mid; D7 hardwire only |
| J1.13 | NC | AC node into R3 via C2 |
| Everything else in the Dn/K/A/GND map | probable | confirmed |
