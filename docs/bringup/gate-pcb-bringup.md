# Gate PCB — Bring-up supply card (Type A divider + anode)

**Role:** PASS stamp and operator checklists for bringup-supply sch→PCB (not the
command tutorial).

**Energize:** No. **Prior:** Continuity PASS; Gate **0b** + **0c** schematic **PASS**
([`gate-0-sch-verify.md`](gate-0-sch-verify.md), [`gate-0-spice.md`](gate-0-spice.md)).

**Shared process:** skill `kicad-gated-sch-pcb`.  
**Instance binding:** [`design-process.md`](design-process.md).  
**Verify commands:** [`../../hardware/pmt-interface/AGENTS.md`](../../hardware/pmt-interface/AGENTS.md).

Board: [`../../hardware/pmt-interface/bringup-supply.kicad_pcb`](../../hardware/pmt-interface/bringup-supply.kicad_pcb)
(rev `0.4-route`).  
Schematic: [`../../hardware/pmt-interface/bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch).

Filter clone is outside this ladder. **Do not invent operator OK.**

## Status

| Sub-gate | Who | Status |
|---|---|---|
| 1 Generate / edit bringup-supply sch | agent/operator | **mech OK** |
| 2 Auto-validate nets / ERC | agent | **mech OK** — tracked `--validate` |
| 3 Operator verifies schematic | operator | **PASS** (= Gate 0b) — **commit `.kicad_sch`** |
| 4 PCB component placement draft | agent/operator | **mech OK** — operator placement saved |
| 5 Operator verifies rotation + position | operator | **PASS** (2026-11-02) |
| 6 Snap to 2.54 mm | agent | **mech OK** |
| 7 Wire K/−HV + GND | agent | **mech OK** — F.Cu=K, B.Cu=GND |
| 8 Wire dynode / anode signals | agent | **mech OK** — InN / JumperN |
| 9 Auto DRC | agent | **mech OK** — 0 shorts / 0 unconnected |
| 10 Operator verifies route + stuff OK | operator | **PASS** (2026-11-02) |

**Gate PCB overall:** **PASS** (2026-11-02) — rev `0.4-route`, DRC clean.

Mech verify commands (after each agent step): [`../../hardware/pmt-interface/AGENTS.md`](../../hardware/pmt-interface/AGENTS.md); skill `kicad-gated-sch-pcb`. Force regenerators only with explicit operator ask.

## Operator checklist — Gate 3 (schematic)

Satisfied by [`gate-0-sch-verify.md`](gate-0-sch-verify.md) **PASS**. Keep the tracked sheet; re-run `--validate` after manual edits.

## Operator checklist — Gate 5 (placement)

Open the **tracked** PCB in Pcbnew. Place/rotate as needed, **save**, then confirm:

| # | Check | Pass |
|---|---|---|
| 1 | J3.1 = K (−HV), J3.2 = GND | [x] |
| 2 | Divider order R10…R18 K→GND; Rbleed across K–GND | [x] |
| 3 | J4 wrap: .7=K, .8=D1, .9=D2, .6=D3, .5=D4, .4=D5, .12=D6, .3=D7, .2=D8, .14=GND | [x] |
| 4 | J4.1/10/11/13 unnetted NC | [x] |
| 5 | Anode cluster after rotate: A→R19/JMP_DC/C4(DNP)→J5 | [x] |
| 6 | Creepage / stuffing access OK; file saved for git | [x] |

**PASS** (operator 2026-11-02).

## Operator checklist — Gate 10 (route + stuff readiness)

| # | Check | Pass |
|---|---|---|
| 1 | K/−HV and GND on dedicated layers; dynodes/SCOPE not shorting | [x] |
| 2 | DRC mech clean on routed nets | [x] |
| 3 | Matches [`bom-divider.md`](bom-divider.md) stuffing map | [x] |
| 4 | Operator OK to **stuff** (Gate A); still **0 V** | [x] |

**PASS** (operator 2026-11-02).

## Sign-off

| Field | Value |
|---|---|
| Date | 2026-11-02 |
| Operator | operator |
| Gate 3 | **PASS** (0b) |
| Gate 5 | **PASS** |
| Gate 10 | **PASS** |
| Result | **PASS** |

**Next:** [`gate-a-build.md`](gate-a-build.md) (stuff 2.2M/3.3M; sch stays equivalents; still **0 V**).
