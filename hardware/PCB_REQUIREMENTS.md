# Custom PCB requirements and status

Status (28 September): **four-layer revision B CAD and fabrication exports are available** in `pcb/wattsense-main-revB-4layer/`. The original two-layer revision A remains in `pcb/wattsense-main/` as a budget alternative. Open the selected revision's README for the checked design, matching BOM and remaining physical validation. The board integrates the INA219 ICs and fan driver; the ESP32, converter, protected pack and charger remain external. Revision B adds two internal GND planes, 57 GND stitching vias and 2.2 kOhm I2C pull-ups. The 2 A path ceiling is unchanged.

The five-day review should not depend on fabrication delivery. Use the software demonstration and CAD design, plus any honestly completed lab work. The prototype uses cabled interfaces instead of unverified module sockets. Check the selected external hardware before assembly and revise the design if measurements require it.

## Implemented functions

- Cabled interface to an external ESP32 development board, preserving access to its USB connector.
- Three native INA219AIDR SOIC-8 ICs for battery, converter and charger-output measurement.
- Fused 5 V distribution and load branches, plus battery terminals for an externally fused/disconnected pack. The near-pack fuse and manual disconnect are external and mandatory.
- Connection to a bought 5 V converter, with clearly identified power domains.
- One AO3400A optional-load channel with gate pulldown and SS14 flyback diode.
- DS18B20 connector and two local button connectors.
- Four test points for GND, 3V3, system supply and fan gate. I2C is available at the signal header.
- Mounting holes, polarity labels, connector names and revision number.

The purchased battery/BMS, enclosed charger and solar controller remain external. This board is not a custom BMS or mains power supply.

## Information required to release a layout

| Input | Current status |
| --- | --- |
| Exact ESP32 board and pin availability | Not purchased; cable connector avoids module footprint dependence |
| Sensor IC packages and terminal layout | Selected in CAD; purchased parts/fit still unverified |
| Converter current/thermal performance and mounting | Not measured |
| Fan startup current and driver design | Not measured |
| Final pack and charger connector arrangement | Not selected |
| Enclosure dimensions | Not selected |

Both revisions avoid dependency on ESP32/converter mounting dimensions by using cable connectors. Their IC and connector footprints are selected against documented package families. Exact purchased parts, substitutions, external power ratings and enclosure fit still require verification.

## Checks and outputs

1. Complete schematic and component calculations.
2. Verified footprints and connector polarity.
3. Appropriate trace widths, copper, current loops and measurement routing.
4. ESP32 antenna clearance according to the exact board/module guide.
5. Accessible fuses, test points and programming connector.
6. Resolved electrical and layout rule violations.
7. Exported Gerber/drill files and fabrication drawing.
8. BOM, assembly instructions and board bring-up record.
9. Repeat calibration and controller tests on the assembled board.

CAD is complete as a prototype candidate. Obtain actual fabrication/component quotes before selecting a revision, allow time for assembly/rework and follow the matching bring-up guide. A secure module/perfboard assembly remains the fallback if cost or lead time prevents fabrication. See `../docs/SIMULATION_REPORT.md` for completed checks and the limits of the reduced simulation models.
