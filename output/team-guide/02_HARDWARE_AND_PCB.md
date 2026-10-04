# WattSense: hardware and PCB guide

**As of 2 October 2026.** The native Rev B schematic and `ASSEMBLY_AND_BRINGUP.md` take precedence for assembly. No physical hardware has been tested. Results below are from the **30 September audit**, not new tests.

## 1. What we buy and what we designed

We need **one custom interface PCB**. We do **not** need to design a BMS.

| Purchased item | Its job |
| --- | --- |
| Protected common-port 4S LiFePO4 pack, nominal 12.8 V | Stores energy; its internal BMS provides cell protection |
| Charger specified for that exact pack | Regulates charging |
| Non-isolated regulated 5 V buck converter | Reduces battery voltage for the loads |
| Classic ESP32 development board | Runs measurement, estimation and control software |
| DS18B20, small 5 V lamp and two-wire fan | Temperature measurement and demonstration loads |
| Near-pack DC fuse, disconnect, wiring and enclosure | External protection and assembly |

Our PCB measures energy flow and switches the optional fan; the essential lamp remains connected. Optional solar needs a compatible controller, never a panel connected directly to J2.

## 2. Main parts on our PCB

| Part | Meaning and role |
| --- | --- |
| U1, INA219 at `0x40` | Signed battery current; positive means discharge, negative means charging |
| U2, INA219 at `0x41` | Converter-input current and voltage |
| U3, INA219 at `0x44` | Charger-output measurement; not automatically a solar measurement |
| R1–R3, 0.1 Ω shunts | Small resistors that produce a measurable voltage drop: at 1 A, each drops 0.1 V and dissipates 0.1 W |
| Q1, AO3400A MOSFET | Electronic switch in the fan's negative return |
| Gate resistor and pulldown | Limit gate-drive pulse and make the fan default OFF during reset/disconnection |
| Fuses, TVS and flyback diode | Different protection functions; none replaces correct wiring or external protection |
| Capacitors, pull-ups and connectors | Supply filtering, communication and external connections |

Use **INA219AIDR SOIC-8 ICs**, not breakout modules or the differently pinned DCN package. Separate sense tracks leave each two-terminal shunt's pads; these are not four-terminal shunts.

## 3. How the PCB was designed

A **schematic** defines which electrical pins connect. A **footprint** is a component's physical pad pattern. The **layout** places those footprints and copper tracks on the board; **vias** connect copper between layers. **Gerbers and drill files** describe the board to the fabricator.

1. Define components, connections, packages and placement using a Python-assisted KiCad generator.
2. Generate editable CAD files; route signals with a custom script and explicit power paths.
3. Upgrade the initial two-layer design to **Rev B: 100 × 90 mm, four copper layers**. Top and bottom carry routing; both inner layers are ground planes.
4. Add **57 ground stitching vias**, connecting ground across layers; 104 vias total.
5. Change I²C pull-ups from 4.7 kΩ to **2.2 kΩ** after RC simulation predicted excessive rise time. Actual edges still need checking.
6. Check circuit rules, geometry, connections and exports. Generate Gerbers, drills and component list.

Main supply tracks are 1.5 mm; signals typically 0.25 mm. These dimensions do **not** establish temperature rise, noise immunity or current capacity. Native KiCad files are authoritative; never regenerate over manual edits.

## 4. Connector map: read before wiring

Pin 1 is the square through-hole pad. Confirm PCB numbering, not plug orientation. **J3 carries battery voltage; J4 carries 5 V.**

| Connector | Pin 1 | Pin 2 | Other detail |
| --- | --- | --- | --- |
| J1 BATTERY | Protected pack positive, after fuse/disconnect | Protected pack negative P− | Never raw cell B− |
| J2 CHARGER | Charger positive | Charger negative/GND | One matched charging source |
| J3 TO BUCK | Converter input positive | Converter input negative | Battery-level DC |
| J4 FROM BUCK | Regulated 5 V positive | Converter output negative | Verify voltage first |
| J5 LAMP | Fused lamp positive | GND | Essential branch |
| J6 FAN | Fused fan positive | Switched fan return | Pin 2 is **not GND** |
| J8 TEMP | 3.3 V | DS18B20 data | Pin 3 = GND |
| J9 LOAD | GPIO27/button signal | GND | Normally-open button |
| J10 FULL | GPIO26/button signal | GND | Full-reference procedure only |
| JP1 | 5 V rail | ESP32 supply net | Removable jumper, open by default |
| J11 ESP POWER | Optional ESP32 5 V feed | GND | Active only with JP1 fitted |

**J7 is a cable header, not an ESP32 socket.** Use a checked cable about 100 mm or shorter.

| J7 pin | Connection |
| --- | --- |
| 1 | ESP32 3V3 output, supplying sensor logic |
| 2 | ESP32 GND |
| 3 | SDA → GPIO21 |
| 4 | SCL → GPIO22 |
| 5 | FAN_EN → GPIO25 |
| 6 | TEMP_DQ → GPIO4 |
| 7 | BTN_LOAD → GPIO27 |
| 8 | BTN_FULL → GPIO26 |

No 5 V signal belongs on J7. Test points: TP1=GND, TP2=3V3, TP3=battery-level SYS_P, TP4=fan gate.

## 5. Limits, grounds and USB

- Intended ceilings: **2 A battery path**, **1.5 A continuous total at 5 V**, including a battery-powered ESP32. Start with approximately 2.5 W loads; measure each lamp/fan branch at **≤0.6 A**. Qualify startup separately.
- Fit a suitable **DC-rated 2 A fuse near pack positive** and a disconnect. Fuse interruption and derating must suit the actual pack. A fuse or software threshold is not a precision current limiter.
- There is **no reverse-polarity blocking circuit**. Connect only to the protected pack terminals. Separate-port BMS packs require a revised wiring arrangement.
- The fan must be power-only: an extra ground, USB or data connection can bypass its low-side switch. Check bench-supply, oscilloscope-earth and laptop grounding before connection.
- USB development: **JP1 open, J11 disconnected**. Laptop energy is excluded from battery measurements.
- Battery operation: USB disconnected; JP1 fitted and J11 wired to the exact ESP32 board's documented 5 V input. Simultaneous USB logging needs verified VBUS isolation. Use the same arrangement in comparison tests.

## 6. What is checked, and the next bench gates

The September audit found agreement across **50 component locations, 114 electrical pads, 19 nets and 20 power paths**. Configured ERC/DRC reported zero violations. Enabling every category revealed six connector footprint-filter metadata warnings; actual footprints, pin nets, pitch and drill agreed. This is CAD evidence, not physical validation.

Proceed through the full assembly guide:

1. Inspect components, soldering, polarity and unpowered shorts; leave JP1 open.
2. Test logic supply and the dedicated bring-up firmware; confirm all three I²C addresses and fan default-OFF.
3. Test J4 at 5.0 V, initially limited to 100 mA without loads.
4. Test J1 using a 12–13 V bench supply, initially 100 mA with the converter unloaded. Compare readings against an independent meter.
5. Obtain lab review before adding the fused battery. Establish a genuine full-charge reference.
6. Keep `HARDWARE_CONFIRMED=false` until prerequisites pass. Then test controlled switching, startup, faults, temperature and runtime. Stop discharge at the supervised normal endpoint; the lamp is not automatically disconnected.

## Source files in the complete project

Repository-relative paths; request the project folder to open them:

- `hardware/pcb/wattsense-main-revB-4layer/wattsense-main.kicad_pro`
- `hardware/pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md`
- `hardware/pcb/wattsense-main-revB-4layer/DESIGN_NOTES.md`
- `hardware/REFERENCE_WIRING.md`
- `docs/LAB_START_GUIDE.md`
- `docs/evidence/recheck-2026-09-30/hardware/FINDINGS.md`
