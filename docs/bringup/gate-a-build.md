# Gate A — Build divider + anode measurement

**Energize:** No (0 V). **Prior:** Gate 0b + Gate 0c **operator** PASS;
Gate PCB ([`gate-pcb-bringup.md`](gate-pcb-bringup.md)) Gate **10** **PASS**.
**Status:** Open — ready to stuff.

Page-2 stays on **segment equivalents** (R10=4.4M … R18=1.1M) for sim / validate /
test. Gate A **assembles**; Gate B is the first measurement of stuffed networks.
Stuff sourced **2.2 MΩ / 3.3 MΩ** per [`bom-divider.md`](bom-divider.md) + page-2
**STUFF:** notes — **no R10A sch redraw**.

## Goal

Physically assemble the bring-up card/harness before any HV. Stages 1–5 must not
depend on Pico, LED, or HV-sense population.

## Build checklist

| Step | Action | Done |
|---|---|---|
| 1 | Read stuffing map in [`bom-divider.md`](bom-divider.md) + page-2 “STUFF:” notes | [ ] |
| 2 | Verify part markings vs shopping list before solder | [ ] |
| 3 | Stuff Type A string: R10 as 2×2.2M series; R11–R13 = 3.3M; R14–R17 = 2.2M; R18 as 2×2.2M ∥ | [ ] |
| 4 | Install HV input J3; soft bleed Rbleed ≥22 M (value non-critical; string already bleeds); polarity −HV / GND | [ ] |
| 5 | Install mate **J4** (wrap 2×7, 7.62 mm) for tube-board **J1**; strain-relieve harness | [ ] |
| 6 | Confirm J4: .7=K, .8=D1, .9=D2, .6=D3, .5=D4, .4=D5, .12=D6, .3=D7, .2=D8, .14=GND | [ ] |
| 7 | Leave J4.13 unconnected to HV (filter AC on tube board only) | [ ] |
| 8 | Install anode BNC J5; center←A, shell←GND; JMP_DC for DC default | [ ] |
| 9 | Leave HV-sense R20/R21 and Pico/LED **DNP** unless building ahead | [ ] |
| 10 | Do **not** stuff sim-only Vhv / Iph / Ra / Ca (Ra models stock page-1 R2) | [ ] |
| 11 | Visual: no bridges, creepage on −HV, labels readable | [ ] |
| 12 | Photo of stuffed board (optional evidence) | [ ] |

## Do not

- Redraw the sch as R10A/R18A networks (breaks Gate 0c KiCad fidelity).
- Apply HV or connect the variable regulated PSU for “quick checks.”
- Tie anode into the D8–GND divider end.
- Use ribbon Odd/Even numbering for J4.

## Exit Gate A

- [ ] Assembly matches equiv designators + stuffing artifact
- [ ] Mate connector pinout documented / labeled
- [ ] Anode BNC path present
- [ ] Still **0 V**

**Next:** [gate-b-cold.md](gate-b-cold.md) (first measure of stuffed networks)
