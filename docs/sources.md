# Sources

Local copies live in [`datasheets/`](datasheets/). There is **no public OEM schematic** for the Philips/Photonis medical I/O filter PCB on this XP3312/SQ; reverse-engineering uses the tube datasheet, sibling-board notes, photos, and continuity.

## Tube

| File | What it establishes |
|---|---|
| [XP3312.pdf](datasheets/XP3312.pdf) | Photonis XP3312 datasheet: 8-stage 76 mm tube, divider ratios Type A, limiting values, outline + pin legend (`K`, `Dn`, `A`, `sp`, `ic`) |
| [XP3312-outline-pins-left.png](datasheets/XP3312-outline-pins-left.png) | Crop of flying-lead / FE2019-style pin circle from the datasheet |
| [XP3312-outline-pins-right.png](datasheets/XP3312-outline-pins-right.png) | Crop of XP3312B JEDEC B14-38 pin circle |

**This unit (from label photos):** Photonis XP3312/SQ, SN 294056, batch 04229, 29-Sep-04, PH 36 pC, PHR 8.7%, Made in France.

## Board architecture (no OEM datasheet)

| File | What it establishes |
|---|---|
| [Prutchi-XP3312-PMT-Probe.pdf](datasheets/Prutchi-XP3312-PMT-Probe.pdf) | DIY Physics TN 2013-2: XP3312/SQ flying-lead pinout (Fig. 4), DIY divider (Fig. 6), notes that the stock Philips base PCB is normally removed; keep blue ~4700 pF HV capacitor |
| [Prutchi-XP2422-PMT-Probe.pdf](datasheets/Prutchi-XP2422-PMT-Probe.pdf) | Same *class* of medical base board: SMB/coax AC-coupled anode out, last-dynode bypass caps, **14-pin (2×7) wrap-numbered socket** (Fig. 3: `1‥7 | 14‥8`). Electrode→pin map is XP2422-specific — **not** our XP3312 assignments |
| [Photonis-PMT-Catalogue.pdf](datasheets/Photonis-PMT-Catalogue.pdf) | Catalog context (XP3312 family, sockets FE1014/FE2019, VD282K) |

## Photos

See [`img/README.md`](img/README.md), [`photo-bom.md`](photo-bom.md), and [`photo-trace-map.md`](photo-trace-map.md).

## Upstream URLs

- https://www.diyphysics.com/wp-content/uploads/2013/01/XP3312.pdf
- https://www.diyphysics.com/wp-content/uploads/2013/02/Philips-XP23312-PMT-Probe.pdf
- https://www.diyphysics.com/wp-content/uploads/2013/04/Philips-XP2422_SN-PMT-Probe.pdf
- https://hallcweb.jlab.org/DocDB/0008/000809/001/PhotonisCatalog.pdf
