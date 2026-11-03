# Bring-up supply — gated sch/PCB instance binding

**Role:** thin board binding for `bringup-supply`. Canonical ladder, host vs
operator, verify-after-each-step, and overwrite rules: personal skill
**`kicad-gated-sch-pcb`**. Exact commands: [`../../hardware/pmt-interface/AGENTS.md`](../../hardware/pmt-interface/AGENTS.md).  
PASS stamp: [`gate-pcb-bringup.md`](gate-pcb-bringup.md).

## Tracked artifacts (this board)

| Artifact | Path | After operator OK |
| --- | --- | --- |
| Schematic | [`bringup-supply.kicad_sch`](../../hardware/pmt-interface/bringup-supply.kicad_sch) | Tracked file wins |
| PCB | [`bringup-supply.kicad_pcb`](../../hardware/pmt-interface/bringup-supply.kicad_pcb) | Tracked file wins |
| Project | [`bringup-supply.kicad_pro`](../../hardware/pmt-interface/bringup-supply.kicad_pro) | Tracked with the board |

## Ladder mapping

| Skill gate | This project |
| --- | --- |
| Gate 3 (sch STOP) | Gate **0b** ([`gate-0-sch-verify.md`](gate-0-sch-verify.md)) |
| Gate 10 (route STOP) | Unlocks Gate A ([`gate-a-build.md`](gate-a-build.md)); still **0 V** |

Filter clone [`pmt-interface.kicad_pcb`](../../hardware/pmt-interface/pmt-interface.kicad_pcb) is **outside** this ladder.

## Layer policy

| Layer | Use |
| --- | --- |
| F.Cu | K (−HV) |
| B.Cu | GND |
| InN / JumperN | Dynode / anode / SCOPE |

Re-entry after move: Gate **5** → `--snap` → `--route` → DRC → Gate **10** (commands in AGENTS).
