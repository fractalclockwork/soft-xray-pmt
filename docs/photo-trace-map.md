# Photo trace map

Working connectivity is in [`probable-netlist.md`](probable-netlist.md) / [`pin-reconciliation.md`](pin-reconciliation.md) (**continuity-verified**). Photos locate parts and traces; they did not uniquely resolve the filter-cap nets — DMM did.

## Observed board topology

```text
  tube flying leads  -->  perimeter pads  -->  1:1 traces  -->  J1 2x7 header
                                                      |
                                                      +--> coax J2 (anode)
                                                      +--> C_HV / R_K on cathode
                                                      +--> C2/C3 + R3 filter: D8 & J1.13 → mid → GND
```

| Observation | Photos | Implication |
|---|---|---|
| Dual-row header, 7+7 fillets | IMG_7005, 7020 | J1 = **2×7 / 14 pins** |
| Radial traces pad→header | IMG_7020, 7014, 7015 | Dynodes mostly hardwired breakout |
| Gold coax, center toward board | IMG_7001, 7002, 7020 | Anode signal out |
| Blue disc `472Z 2KV` | IMG_7006 | C1 on cathode path |
| SMD `1001` near blue cap | IMG_6989, 7006 | R1 1 kΩ with K |
| SMD `115` | IMG_7005 | R2 ~1.1 MΩ anode load |
| Two tan MLCCs + `100` | IMG_7005, 6993 | Filter cluster; **continuity**: one cap on **D8**, other on **J1.13**, R3 to **GND** |

## Datasheet pin lock

Prutchi Fig. 4 / XP3312 outline: **K=16, A=12, D1=1, D2=3, D3=4, D4=7, D5=8, D6=9, D7=10, D8=11** — matches bottom-up CW count confirmed on this board.

## J1 NC candidates (photo vs continuity)

Schematic marks **J1.1 / 10 / 11** `no_connect`. Sharpest header photos (`IMG_7001`, `IMG_7002`):

| J1 pin | Photo | PCB action |
|---|---|---|
| **1** | No clear fan-out on F.Cu under plastic (outer end opposite 7/8) | pad only, no copper out |
| **10** | Mid right-row pin; no clear fan-out | pad only, no copper out |
| **11** | Next to wired **12** (D6); glare/housing often hides pad | pad only, no copper out; **least clear — DMM required** |

All other J1 pins show radial/filter copper consistent with the verified netlist. Photo “open” is not a substitute for beeping 1/10/11 free of tube/GND.

## KiCad 2-layer clone

Generator: [`hardware/pmt-interface/gen_pcb.py`](../hardware/pmt-interface/gen_pcb.py) → [`pmt-interface.kicad_pcb`](../hardware/pmt-interface/pmt-interface.kicad_pcb).

| Item | Photo match |
|---|---|
| **J1** | DIP-14–class **wide IC socket** (7.62 mm rows, wrap 1–7\|14–8) — not IDC ribbon |
| **B.Cu** | H/V/45 dynode fan-out tube→J1 (header/plastic side; IMG_7002/7020) |
| **F.Cu** | Filter trio in DIP channel; C1/R1 at K; D8+C3; A→R2; GND rim→J1.14 |
| **Edge.Cuts** | ~Ø44 mm (pin circle 31.8 mm + thin rim) |

J1.1/10/11 are pads with **no copper out**. Preview: [`pmt-interface-pcb.pdf`](pmt-interface-pcb.pdf) / [`.svg`](pmt-interface-pcb.svg).

Concentric **ring-lane** routing (for other circular breakouts) is documented in the personal skill `pcb-ring-lane-routing`; this clone uses photo H/V/45 lands.
