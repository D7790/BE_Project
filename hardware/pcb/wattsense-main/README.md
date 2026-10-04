# Wattsense main PCB - revision A

**One custom board is required for this version.** It integrates three current monitors, the optional-load MOSFET, fuses, transient suppression, temperature/button interfaces and power distribution. The ESP32 board, 5 V converter, protected battery pack and matched charger remain external.

Status: **engineering prototype, not physically validated**. See `reports/VALIDATION.md` for the final design-check results. Fabrication files are for a first prototype; no hardware accuracy, thermal or reliability results are claimed.

## Open and inspect

Open `wattsense-main.kicad_pro` in KiCad 10. Open its schematic and PCB from the project manager. All sources are editable; Python is not required to use them. The project-local symbol library is included. PCB footprints are embedded in the board and use the standard KiCad libraries.

| File | Purpose |
| --- | --- |
| wattsense-main.kicad_sch | Complete native schematic |
| wattsense-main.kicad_pcb | Routed two-layer PCB |
| wattsense-main.kicad_pro | Project and design rules |
| exports/schematic.pdf | Printable A3 schematic |
| exports/board-top.png | Board preview |
| exports/gerbers/ | Prototype Gerber and drill files |
| exports/wattsense-main-revA-prototype.zip | Fabricator archive, generated after passing checks |
| BOM.csv | Component-level purchasing list |
| BOM-grouped.csv | Quantities grouped by component type for purchasing |
| ASSEMBLY_AND_BRINGUP.md | Wiring, assembly and measured acceptance checks |
| DESIGN_NOTES.md | Calculations, limits, component choices and references |
| reports/ | ERC, DRC, connectivity audit and recorded validation status |
| check_and_export.ps1 | Rerun checks and rebuild prototype fabrication outputs |
| open_project.ps1 | Open this project in the installed KiCad 10 manager |

## What is designed

- 100 x 90 mm, two-layer FR-4, 1.6 mm thickness, 1 oz outer copper.
- U1/U2/U3: **INA219AID, SOIC-8**, with 0.1-ohm 1 W shunts. Addresses 0x40, 0x41 and 0x44 respectively. This replaces the three breakout boards from the module-based shopping list.
- Battery/distribution path designed around 2 A maximum, with 1.5 mm main tracks. The required battery fuse and manual disconnect are external, close to the pack.
- External regulated 5 V input. F1 is a 2 A fuse; F2/F3 are 1 A branch fuses. Start with a lamp and a fan drawing no more than 0.6 A each. Keep total continuous 5 V current, including any ESP32 supply, at or below 1.5 A and verify temperature/current derating.
- AO3400A low-side fan switch, 330-ohm gate resistor, 47-kilohm hardware pulldown and SS14 flyback diode. A stopped controller defaults the optional output off when the GPIO is high impedance.
- Short cabled ESP32 interface, powered DS18B20 connector, two local-button connectors, four test points and four M3 mounting holes.
- Normally-open jumper JP1 for optional ESP32 5 V power. Remove JP1 before connecting ordinary USB power.

No additional custom BMS, solar-charger, mains or buck-converter PCB is required. These would add substantial development work without being necessary for the selected project objective.

## Before spending money

1. Use the **PCB BOM** for the custom build; do not also purchase three INA219 modules or a separate fan-driver module.
2. Check the exact packages before substitution. In particular, INA219 SOIC and SOT-23 pin assignments differ, and a 0603 fuse does not fit this board's 1206 fuse pads.
3. Print the fabrication/assembly layout at 1:1 and check the purchased connectors, capacitor and IC packages against it. Compare substitute component drawings, not only product photographs.
4. Obtain delivered PCB and component quotes. The earlier project-wide Rs 9,500 allowance covered modules and does **not** establish the cost of this custom board. Buy battery-only hardware first; borrow/defer the solar panel if needed to keep the complete project below Rs 10,000.
5. Have the lab supervisor review the schematic and the selected pack/charger wiring before battery bring-up. This is an untested student prototype, so first power comes from a current-limited bench supply.

The five-day review should not depend on PCB delivery. Show the editable schematic, routed board, check reports and honest software demonstration while the prototype is being assembled.

## Reproducibility

The construction scripts in `tools/` use KiCad's bundled Python and numpy. **They overwrite the generated design**, so do not rerun them over manual edits. The native schematic/PCB are the deliverables. After any manual edit, rerun ERC, DRC with schematic parity, regenerate exports and repeat the physical checks affected by that change.

No board has been ordered, no components have been purchased and no payment has been made.
