# Photo BOM — stock XP3312/SQ I/O filter board

Confidence: `FROM_PHOTO` unless noted. Values preferred over pencil notes when they conflict.

## Tube

| Field | Value | Source |
|---|---|---|
| Maker | PHOTONIS imaging sensors | IMG_6985 / 6998 |
| Type | XP3312/SQ | label |
| Date | 29-Sep-04 | label |
| Batch | 04229 | label |
| SN | 294056 | label |
| PH | 36 pC | label |
| PHR | 8.7% | label |
| Origin | Made in France | label |
| Side code | 331117031963 | label |

## Passive components on filter PCB

| Ref (draft) | Marking | Interpreted value | Role (hypothesis) | Photos |
|---|---|---|---|---|
| R1 / R_K | `1001` | **1 kΩ** | Cathode path series to header pin 7 | 6989, 7006 |
| R2 / R_A | `115` | **1.1 MΩ** | Anode load to GND (notes said 1 M) | 7005 |
| R3 / R_F | `100` | **10 Ω** | Mid-node → GND (between two filter MLCCs) | 7005 |
| C1 / C_HV | `472Z` `2KV` | **4.7 nF, Z tol, 2 kV** | Cathode bypass to GND | **7006** |
| C2 / C_F1 | unmarked tan MLCC | TBD (measure / mark) | **J1.13** ↔ filter mid (continuity) | 6993, 7005 |
| C3 / C_F2 | unmarked tan MLCC | TBD | **D8** ↔ filter mid (continuity) | 6993, 7005 |

## Connectors

| Ref | Description | Notes |
|---|---|---|
| J1 | **Wide IC / DIP-14 style socket** (≈7.62 mm row spacing, two rows of 7) | **Wrap numbering** (1–7 \| 14–8) like Prutchi XP2422 Fig. 3 / DIP-14; **not** IDC ribbon Odd/Even or 2.54 mm dual-row header body |
| J2 | Gold coax (SMA/SMB-style) | Center = anode signal; shell = GND |

## Mechanical

- Circular green PCB on three black standoffs at tube base
- Flying leads from tube soldered to perimeter pads
- Board is **filter + breakout**, not a full dynode divider (matches Prutchi / community)
