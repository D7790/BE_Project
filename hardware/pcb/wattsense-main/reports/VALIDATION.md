# Revision A CAD validation

Checked on 27 September 2026 using installed KiCad 10.0.6. These are design-file checks, not physical test results.

| Check | Result |
| --- | --- |
| Schematic electrical rules (ERC) | 0 reported violations |
| PCB design rules (DRC) | 0 reported errors or warnings |
| Unrouted connections | 0 |
| Schematic-to-PCB parity | 0 mismatches |
| Manifest / exported schematic / PCB pin-net comparison | All 114 electrical pad assignments match |
| Critical IC, MOSFET, diode, shunt and connector pin mapping assertions | Passed |
| PCB size / layer count | 100 x 90 mm / two copper layers |
| Component locations | 50, including connectors, test points and mounting holes |
| Plated holes | 80 total, including 47 signal vias |
| Unplated holes | Four 3.2 mm mounting holes |
| Gerber/drill archive | Required files present, metric units checked, drill counts/bounds checked, ZIP integrity checked |
| Schematic PDF | Rendered and visually inspected; overlapping labels corrected |
| Board previews | Top and 3D renders inspected for component placement, labels and access |

Machine-readable records: erc.json, drc.json, schematic.net.xml and connectivity-audit.json. The latter records SHA-256 hashes of the checked schematic, PCB, project and BOM. No reported violation was marked as an exclusion. KiCad's default ignored categories remain listed in drc.json (including unused tuning-profile checks); a zero count does not mean every conceivable manufacturing or electrical condition was simulated.

The routing uses off-pad vias. Unused one-layer escape vias and the resulting unused escape stubs were removed; checks were rerun. Main supply routes are on the top copper layer; ground pours reinforce the explicit current returns.

## Still required on actual hardware

- Purchased-part footprint/lead/connector fit, solder quality and component authenticity.
- Pack/BMS/charger compatibility and fault-current coordination of the external fuse.
- Power-up, reset, missing-sensor and optional-load-off behaviour.
- Converter regulation, fan startup current, fuse pulse/temperature derating and thermal rise.
- Meter-based current/voltage calibration, charge/discharge sign and useful-capacity measurement.
- Actual runtime-prediction error and controlled-versus-baseline essential-load runtime.
- Enclosure strain relief, wiring polarity and final USB power arrangement.

There is no assembled board, no order and no measured battery result. The existing firmware compiled in the earlier software work, but has not executed on this board. Keep its physical-control lock disabled until the bring-up guide's checks are completed.
