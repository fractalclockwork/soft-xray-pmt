#!/usr/bin/env bash
# Gate 0c — bringup SPICE from the KiCad page-2 schematic (not hand decks).
# Flow: kicad-cli spice export → OP taps → TRAN anode pulse → pass/fail.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$ROOT/../.." && pwd)"
SCH="$REPO/hardware/pmt-interface/bringup-supply.kicad_sch"
OUT="$ROOT/kicad-out"
mkdir -p "$OUT"
cd "$ROOT"
fail=0

echo "=== kicad-cli spice export (bringup-supply.kicad_sch) ==="
kicad-cli sch export netlist --format spice -o "$OUT/bringup-supply.cir" "$SCH"
if grep -E '__[A-Za-z0-9]' "$OUT/bringup-supply.cir" >/dev/null; then
  echo "FAIL: unmodeled spice stubs remain (exclude_from_sim / Sim.Device missing):"
  grep -E '__[A-Za-z0-9]' "$OUT/bringup-supply.cir" || true
  fail=1
fi
for need in Vhv Iph Ra R10 Ca; do
  if ! grep -qE "^${need} " "$OUT/bringup-supply.cir"; then
    echo "FAIL: ${need} missing from KiCad export"
    fail=1
  fi
done
echo "exported $OUT/bringup-supply.cir ($(wc -l < "$OUT/bringup-supply.cir") lines)"
cat "$OUT/bringup-supply.cir"

python3 - "$OUT" <<'PY'
"""Build OP/TRAN decks from KiCad body; avoid shell $ escaping of ngspice $&vars."""
import pathlib, sys
out = pathlib.Path(sys.argv[1])
raw = (out / "bringup-supply.cir").read_text().splitlines()
skip = {".end", ".control", ".endc", ".op", ".tran"}
body = []
for line in raw:
    s = line.strip()
    if not s:
        continue
    if s.split()[0].lower() in skip or s.startswith(".tran") or s.startswith(".op"):
        continue
    if s.startswith("pre_osdi") or s.startswith("run") or s.startswith("plot"):
        continue
    body.append(line)
body_txt = "\n".join(body)

# Global labels export as bare K/D1/A (no KiCad "/" prefix)
op = f"""* Gate 0c OP — KiCad bringup-supply
{body_txt}
.control
  op
  echo TAP_K = $&v(K)
  echo TAP_D1 = $&v(D1)
  echo TAP_D2 = $&v(D2)
  echo TAP_D3 = $&v(D3)
  echo TAP_D4 = $&v(D4)
  echo TAP_D5 = $&v(D5)
  echo TAP_D6 = $&v(D6)
  echo TAP_D7 = $&v(D7)
  echo TAP_D8 = $&v(D8)
  echo I_VHV = $&i(Vhv)
.endc
.end
"""
(out / "op_check.cir").write_text(op)

tran = f"""* Gate 0c TRAN — anode photon pulse from KiCad bringup-supply
{body_txt}
.tran 0.2n 200n
.control
  run
  meas tran a_min MIN v(A) from=40n to=120n
  meas tran a_max MAX v(A) from=40n to=120n
  echo A_MIN = $&a_min
  echo A_MAX = $&a_max
.endc
.end
"""
(out / "tran_check.cir").write_text(tran)
print("wrote op_check.cir + tran_check.cir")
PY

echo
echo "=== OP: Type A divider taps (KiCad netlist) ==="
div_out=$(ngspice -b "$OUT/op_check.cir" 2>&1) || true
echo "$div_out" | grep -E '^(TAP_|I_VHV|Error|Warning)' || echo "$div_out" | tail -30

d1=$(echo "$div_out" | sed -n 's/^TAP_D1 = //p' | tr -d ' ' | tail -1)
d8=$(echo "$div_out" | sed -n 's/^TAP_D8 = //p' | tr -d ' ' | tail -1)
iv=$(echo "$div_out" | sed -n 's/^I_VHV = //p' | tr -d ' ' | tail -1)

if ! python3 -c "
d1, d8, i = float('${d1:-nan}'), float('${d8:-nan}'), float('${iv:-nan}')
ok = True
def near(a, b, rel=0.02, abs_eps=1.0):
    return abs(a - b) <= max(abs_eps, abs(b) * rel)
if not near(d1, -818.1818):
    print(f'FAIL: D1={d1} expected ~-818.18'); ok = False
else:
    print('PASS: D1 tap')
if not near(d8, -45.4545):
    print(f'FAIL: D8={d8} expected ~-45.45'); ok = False
else:
    print('PASS: D8 tap')
# Vhv = string (~41uA) + Rbleed 22M (~45uA) ⇒ ~87uA
if not (70e-6 <= abs(i) <= 105e-6):
    print(f'FAIL: I_VHV={i} expected ~87uA (string+bleed)'); ok = False
else:
    print(f'PASS: I_VHV |I|={abs(i)*1e6:.2f} uA (string+bleed)')
raise SystemExit(0 if ok else 1)
"; then
  fail=1
fi

echo
echo "=== TRAN: anode photon pulse (KiCad netlist) ==="
an_out=$(ngspice -b "$OUT/tran_check.cir" 2>&1) || true
echo "$an_out" | grep -E '^(A_MIN|A_MAX|a_min|a_max|Error)' || true

amin=$(echo "$an_out" | sed -n 's/^A_MIN = //p' | tr -d ' ' | tail -1)
[[ -z "$amin" ]] && amin=$(echo "$an_out" | awk '/^a_min/{print $3; exit}')

if ! python3 -c "
amin = float('''${amin:-}''' or 'nan')
ok = True
if not (amin < -0.1):
    print(f'FAIL: anode min {amin} V — expected negative pulse'); ok = False
else:
    print(f'PASS: anode went negative (min={amin} V)')
# With Ca=15p, peak should be volts-scale, not I*Ra (~kV)
if abs(amin) > 200:
    print(f'FAIL: anode |min| too large {amin} (missing Ca?)'); ok = False
elif abs(amin) >= 0.1:
    print('PASS: anode amplitude plausible')
raise SystemExit(0 if ok else 1)
"; then
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo
  echo "SPICE MECH FAIL (KiCad export path)"
  exit 1
fi
echo
echo "SPICE MECH OK — KiCad bringup-supply netlist: divider taps + anode pulse"
echo "SPICE MECH OK only; Gate 0c PASS requires operator sign-off in docs/bringup/gate-0-spice.md"
exit 0
