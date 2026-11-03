# KiCad bring-up supply — gated PCB instance

**Role:** agent instance for the **Type A HV divider + anode measure** board
(`bringup-supply`), not the stock filter clone. Shared process: skill
**`kicad-gated-sch-pcb`**. Paths / layers / Gate 0b·A map:
[`../../docs/bringup/design-process.md`](../../docs/bringup/design-process.md).  
PASS stamp: [`../../docs/bringup/gate-pcb-bringup.md`](../../docs/bringup/gate-pcb-bringup.md).  
Facts: [`../../docs/bringup/bom-divider.md`](../../docs/bringup/bom-divider.md), Gate 0 / 0b / 0c.

Do **not** invent operator verification; stop at Gates **3**, **5**, and **10**.
Never forge PASS. No `--force-*` without an explicit operator ask.

**Tracked sources of truth (git):** `bringup-supply.kicad_sch`,
`bringup-supply.kicad_pcb`, `bringup-supply.kicad_pro`. After operator OK,
**manual edits win**. Snap/route/validate in place.

Filter analogue [`pmt-interface.kicad_pcb`](pmt-interface.kicad_pcb) is **out of this ladder**.

## Role boundaries

| Allowed | Forbidden |
| --- | --- |
| Validate tracked sch/PCB; `--snap` / `--route` in place | Overwriting Gate-3 sch or Gate-5 PCB with a full regenerator |
| Draft once with `--force-place` / `--force-write` when operator asks | Skipping operator gates; forging PASS |
| Point operator at diffs / DRC reports | Treating ERC/DRC as operator approval |

## Gate flow (do not reorder) — verify after each agent step

```text
[1] Draft schematic                 ← generator once, or operator edit
[2] Auto-validate sch               ← --validate (no write)  → verify OK
[3] Operator verifies schematic     ← STOP → commit tracked .kicad_sch
[4] Draft PCB placement             ← --force-place once, or operator
[5] Operator verifies rot + pos     ← STOP → commit tracked .kicad_pcb
[6] Snap to 2.54 mm                 ← --snap  → verify OK
[7] Wire K/−HV + GND (own layers)   ← --route  → verify OK
[8] Wire dynode / anode signals     ← --route (InN on cross)  → verify OK
[9] Auto DRC                        ← kicad-cli  → 0 shorts/unconnected
[10] Operator verifies route/stuff  ← STOP → commit; then Gate A
```

If parts move after route → Gate **5**, then `--snap` → `--route` → DRC → Gate **10**.

## Schematic (Gates 1–3)

```bash
python3 hardware/pmt-interface/gen_bringup_sch.py --validate
```

Gate **3** = [`../../docs/bringup/gate-0-sch-verify.md`](../../docs/bringup/gate-0-sch-verify.md). After PASS, edit in Eeschema only; re-validate. `--force-write` only if the operator asks to discard the sheet.

## PCB placement (Gates 4–5)

```bash
python3 hardware/pmt-interface/gen_bringup_pcb.py --force-place   # operator-approved wipe only
```

Operator places/rotates in Pcbnew, saves the **tracked** file, confirms Gate **5**. Commit so rotations are not lost.

## Snap + route (Gates 6–9) — never rebuild footprints

```bash
python3 hardware/pmt-interface/gen_bringup_pcb.py --snap    # XY→2.54 mm; rot→90°; clears copper
python3 hardware/pmt-interface/gen_bringup_pcb.py --route   # F.Cu=K, B.Cu=GND, InN=signals
kicad-cli pcb drc --format report --severity-error \
  --output /tmp/bringup-supply-drc.rpt hardware/pmt-interface/bringup-supply.kicad_pcb
```

Require **0** shorting / unconnected-pad errors. DRC ≠ Gate 10.

## Gate 10

Operator confirms route + stuffing readiness (0 V). Stamp [`../../docs/bringup/gate-pcb-bringup.md`](../../docs/bringup/gate-pcb-bringup.md).

## Files

| File | Role |
| --- | --- |
| `bringup-supply.kicad_sch` | Tracked schematic (Gate 3+) |
| `bringup-supply.kicad_pcb` | Tracked PCB (Gate 5+) |
| `bringup-supply.kicad_pro` | Tracked project |
| `gen_bringup_sch.py` | Draft / `--validate` |
| `gen_bringup_pcb.py` | `--force-place` / `--snap` / `--route` |
