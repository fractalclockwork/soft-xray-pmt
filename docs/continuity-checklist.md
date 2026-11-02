# Continuity checklist — stage 1 (unpowered)

Power off. No HV. Use a DMM continuity / resistance mode.  
Verified results: [`pin-reconciliation.md`](pin-reconciliation.md) · netlist: [`probable-netlist.md`](probable-netlist.md) · schematic: [`../hardware/pmt-interface/pmt-interface.kicad_sch`](../hardware/pmt-interface/pmt-interface.kicad_sch).

## Prep

- [x] Open datasheet pin circle: [`datasheets/XP3312.pdf`](datasheets/XP3312.pdf) (Prutchi Fig. 4)
- [x] Open backlight photos: IMG_7020 (header side), IMG_7005 / 7014 (component side)
- [x] Mark physical **pin 1** on J1 relative to coax J2
- [x] **Count J1 pins** = **14 = 2×7**

## 1. Tube orientation (datasheet)

Locate **`sp`**, count **1…19 clockwise** from bottom looking up:

| Tube pin | Expect | OK? |
|---|---|---|
| 1 | D1 | x |
| 3 | D2 | x |
| 4 | D3 | x |
| 7 | D4 | x |
| 8 | D5 | x |
| 9 | D6 | x |
| 10 | D7 | x |
| 11 | D8 | x |
| 12 | A | x |
| 16 | K | x |
| 2,5,6,13–15,17–19 | ic / open | |

## 2. Tube → header

| Electrode | Tube pin | J1 | OK? |
|---|---|---|---|
| D8 | 11 | **2** | x |
| D7 | 10 | **3** | x |
| D5 | 8 | **4** | x |
| D4 | 7 | **5** | x |
| D3 | 4 | **6** | x |
| K | 16 | **7** via ≈1 kΩ | x |
| D1 | 1 | **8** | x |
| D2 | 3 | **9** | x |
| D6 | 9 | **12** | x |
| filter AC | — | **13** via C2 | x |
| GND | — | **14** | x |
| NC? | — | **1, 10, 11** | photo-open; DMM TBD (11 unclear) |

## 3. Coax and anode load

- [x] **A (12) ↔ coax center** (~0 Ω)
- [x] Coax shell ↔ board GND ↔ **J1.14**
- [x] **A → GND ≈ 1 MΩ** (R2 `115`)

## 4. Cathode passives

- [x] **K → R1 (`1001` / 1 kΩ) → J1.7**
- [ ] **K → C1 (`472Z` / 2 kV) → GND** (open/charging at DC) — path identified visually; DC open optional

## 5. Filter cluster (verified topology)

```text
D8 -- C3 --+-- R3 10Ω -- GND
J1.13 -- C2 --+
```

- [x] One tan MLCC between **D8** and mid-node
- [x] Other tan MLCC between **J1.13** and same mid-node
- [x] Mid-node → **`100` / 10 Ω** → GND / J1.14
- [x] Not D7 on the second cap (earlier guess was wrong)

## 6. Close out

- [x] Fill [`pin-reconciliation.md`](pin-reconciliation.md)
- [x] Edit KiCad nets to match reality (bypass = D8 + J1.13)
- [x] Photo-matched 2-layer PCB via `gen_pcb.py` (J1.1/10/11 unrouted)
- [ ] Re-export schematic PDF if desired: `kicad-cli sch export pdf hardware/pmt-interface/pmt-interface.kicad_sch -o docs/pmt-interface-draft.pdf`
- [ ] Hand-clean remaining PCB DRC (silk/clearance/shorts) in pcbnew before fab
