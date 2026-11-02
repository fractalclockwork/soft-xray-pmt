# Stages 7–8 — Pico sense, LED, air-gap

**Prior:** Stage 6 PASS (scope saw controlled pulses). Integration lane last.
Ceilings: [`ceilings.md`](ceilings.md).

---

## Stage 7 — Pico sense + LED

**HV:** ≤ 1000 V first pass. **USB while HV live:** **forbidden**.

### Goal

Local Pico (battery or isolated 3V3) logs HV sense and drives LED per Stage 6
recipe; anode enters a **conditioned** front-end only (peak-hold / stretcher /
comparator) — not raw ~5 ns pulses into the ADC.

### Populate / verify

| Item | Check | Pass |
|---|---|---|
| HV sense R20/R21 fitted; ratio yields ~1–2 V at 1000 V | | [ ] |
| Clamp to ≤3.3 V present | | [ ] |
| Pico powered from battery/iso — host USB unplugged | | [ ] |
| LED driver uses Stage 6 recipe ceilings | | [ ] |
| Anode front-end between coax-A and Pico GPIO/ADC | | [ ] |

### Procedure

1. Gate C dark, then HV to last PASS hold.
2. Log sense-divider reading vs PSU setpoint.
3. Fire LED pulses; log timestamps with anode metrics (peak / stretched width / counts).
4. Abort on sense >3.3 V before clamp, USB attach, saturation, or current abort.
5. Keep WiFi off during HV if using Pico-W (OTA is Stage 8).

### Evidence

| Field | Value |
|---|---|
| HV / sense ADC reading | |
| LED recipe | |
| Anode metrics summary | |
| Power source (battery/iso) | |
| Result | PASS / FAIL |

### Exit Stage 7

- [ ] Sense log correlates with PSU
- [ ] LED + conditioned anode metrics recorded
- [ ] No USB while HV was live

---

## Stage 8 — Air-gap OTA / logging

**OTA / WiFi offload:** **HV = 0 V**, photocathode covered (or documented safe session only).

### Goal

Pico-W inside blackout enclosure stores onboard logs; firmware update and data
pull happen without a USB cable into a live HV domain.

### Constraints

| Topic | Rule |
|---|---|
| OTA HV | `ota_hv_v: 0` — PSU off, bleed settled, cathode covered |
| Enclosure RF | All-metal cans block WiFi — use RF window, plastic/wood box, or open-lid OTA |
| Log contents | Vs sense, LED stimulus, anode metrics, timestamps |
| Arm sequence | OTA → disable radio → close enclosure → Gate C → HV |

### Procedure

1. HV off; confirm 0 V and dark cover.
2. Enable Pico-W SoftAP or known SSID; flash / pull logs.
3. Disable radio; verify onboard log retained.
4. Close blackout; re-run Gate C before any later HV session.

### Evidence

| Field | Value |
|---|---|
| OTA method (SoftAP / SSID / open-lid) | |
| Firmware / log artifact IDs | |
| Confirmed HV was 0 during OTA | |
| Result | PASS / FAIL |

### Exit Stage 8

- [ ] OTA / offload demonstrated at 0 V HV
- [ ] Onboard logging path known for future runs
- [ ] Bring-up ladder complete for first full pass

**Status update:** mark stages PASS in [`README.md`](README.md) when done.
