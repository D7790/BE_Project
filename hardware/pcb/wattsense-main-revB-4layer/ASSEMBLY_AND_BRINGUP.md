# Assembly and bring-up

Revision B, four-layer board: use this directory's BOM and fabrication files. R4/R5 are **2.2 kOhm**, while the 1-Wire pullup R6 remains 4.7 kOhm. Internal GND planes increase the heat needed for ground-terminal soldering. Inspect all joints for proper wetting. On an oscilloscope, check I2C 30%-70% rise time is <=1 us at 100 kHz with the final ESP32 cable; the reduced RC simulation covers capacitance through 400 pF, not arbitrary cable length.

Revision B is a low-voltage laboratory prototype. Use a common-port protected 4S LiFePO4 pack, its matching charger, a non-isolated regulated 5 V converter, and power-only demonstration loads. This PCB does not replace the pack BMS, charge controller or external pack fuse.

## Connector map

Pin 1 is the square pad on through-hole connectors. Identify it from the PCB numbering/assembly drawing; do not infer numbering from which end of a loose plug is facing you.

| Connector | Pin 1 | Pin 2 | Additional pins / purpose |
| --- | --- | --- | --- |
| J1 BATTERY | Protected pack positive **after** near-pack fuse and disconnect | Protected pack negative P- | Never use raw cell B- |
| J2 CHARGER | Matched charger positive | Charger negative / GND | One charger only; either enclosed charger or solar-controller BAT port |
| J3 TO BUCK | Converter input positive, after load shunt | Converter input negative | Raw pack-level DC, not 5 V |
| J4 FROM BUCK | Regulated 5 V output positive | Converter output negative | Check 5.0 V before connection |
| J5 LAMP | Fused essential-load positive | GND | 5 V, initially <= 0.6 A |
| J6 FAN | Fused fan positive | Switched fan return | Not GND; no extra fan ground/data connection |
| J8 TEMP | 3.3 V | DS18B20 DQ | Pin 3 = GND; powered three-wire mode |
| J9 LOAD | GPIO27/button signal | GND | External normally-open button |
| J10 FULL | GPIO26/button signal | GND | External normally-open button; full-reference procedure only |
| JP1 | 5 V rail | ESP32 supply net | Removable jumper; **leave open by default** |
| J11 ESP POWER | Optional ESP32 5 V input feed | GND | Only active with JP1 fitted |

J7 is an eight-pin signal header. Use an individually checked cable no longer than about 100 mm:

| J7 pin | Board net | ESP32 destination |
| --- | --- | --- |
| 1 | 3V3 | ESP32 3V3 output; this powers the monitor ICs |
| 2 | GND | ESP32 GND |
| 3 | SDA | GPIO21 |
| 4 | SCL | GPIO22 |
| 5 | FAN_EN | GPIO25 |
| 6 | TEMP_DQ | GPIO4 |
| 7 | BTN_LOAD | GPIO27 |
| 8 | BTN_FULL | GPIO26 |

J7 is not a direct plug-in ESP32 footprint. The selected ESP32 development board must expose these GPIOs. No 5 V signal is permitted on J7. Keep I2C at 100 kHz initially and check rising edges if cable length or hardware changes.

Test points: TP1 = GND, TP2 = 3V3, TP3 = SYS_P (battery-level distribution voltage), TP4 = FAN_GATE. Probe SYS_P with a meter rated for that DC voltage; never connect it to an ESP32 GPIO.

## Required external protection and source arrangement

- An appropriately DC-rated **2 A fuse near pack P+**, followed by a manual disconnect, before J1. Choose its interrupt rating against the pack's possible fault current; a fuse is not a precision 2 A current limiter.
- A charger compatible with this exact 4S LiFePO4 pack, initially <= 1 A output, connected only at J2. Do not run two chargers in parallel. The solar panel connects to a suitable solar controller, never directly to J2.
- A 5 V converter with documented input range covering the pack and verified output current limiting. Begin the unloaded J4 check at **100 mA**, as in step 4 below; increase deliberately only as the connected load requires. Continuous board loading is limited to 1.5 A at 5 V, including the ESP32 when battery-powered. Qualify startup separately rather than increasing limits to hide a fault.
- Correct polarity throughout. There is **no reverse-polarity blocking circuit** on this board. The TVS suppresses transients; it is not permission to connect reversed leads.
- A common-port pack/BMS arrangement. A pack with separate charge/discharge returns needs a revised system connection diagram; do not bridge its ports by guessing.

All charge/discharge current is measured through R1 when the harness follows this map. U2 measures the converter branch. U3 measures the one charger connection. The shunts slightly reduce voltage reaching the pack/load; verify the pack's actual charge completion behaviour.

## Assembly order

1. Inspect bare PCB dimensions, drill plating, silk polarity and any fabrication defects. Check the 1:1 print against actual components.
2. Solder low-profile parts first: R4-R10, C1-C10, fuses, Q1, D1/D2 and U1-U3. Use magnification/flux for SOIC and SOT-23 pins.
3. Fit R1-R3 current shunts with sound joints across the complete pads. Do not bridge either shunt with solder or wire.
4. Fit C11, headers and terminal blocks. Match C11's positive lead and diode cathode stripes to pad 1. INA219 pin 1 must match the footprint pin-1 mark; Q1 pins are G=1, S=2, D=3.
5. Leave JP1 unbridged. Fit insulating standoffs and strain-relieve the external wires.
6. Clean and inspect joints. Record actual part markings and substitutions in the BOM.

## Measured bring-up sequence

Do not perform a destructive battery short-circuit test. Fault behaviour can be evaluated using software sensor disconnection, limited laboratory sources and controlled loads.

1. **Unpowered:** disconnect every source. Check that 3V3/GND and 5V/GND are not shorted; capacitor charging can make resistance readings change. Confirm J6 pin 2 is not hard-connected to ground. Verify R1/R2/R3 paths with a suitable low-resistance method; a beeping continuity tester alone cannot distinguish a 0.1-ohm shunt from a short.
2. **Logic supply only:** leave J1/J2/J4 unpowered and JP1 open. Apply regulated 3.3 V to the board through the J7 harness with a 30 mA limit, or power the checked ESP32 by USB. Confirm 3.3 V at TP2 and no unexpected heating. Do not drive external 3.3 V into an already-powered ESP32 output.
3. **Bus test:** use the dedicated `bringup` firmware described in the root `docs/LAB_START_GUIDE.md`. It scans at 100 kHz and holds GPIO25 low. Require exactly the expected monitor addresses 0x40, 0x41, 0x44 (plus any deliberately connected devices). Check temperature plausibility and both button inputs. No pull-ups to 5 V are permitted.
4. **5 V load side only:** apply 5.0 V at J4 with a 100 mA current limit and no loads. Confirm JP1 open means J11 is not driven by the 5 V rail. Fit a small resistive/LED load, raise the limit deliberately, and check branch fuse/connector polarity.
5. **Fan default-off:** with GPIO25 disconnected or the ESP32 held in reset, measure TP4 near 0 V and verify the optional load is off. A high-impedance meter can show a floating return voltage when off; verify actual load current as well.
6. **Battery-side bench test:** with no battery or charger connected, use a current-limited 12-13 V bench supply at J1, starting at 100 mA with the converter unloaded. Increase gradually for known essential-branch loads; the diagnostic build keeps the fan off. Compare U1 and U2 against a reference meter at zero and several loads. Confirm positive U1 current means discharge. Record calibration readings following `docs/LAB_START_GUIDE.md` before applying candidate corrections.
7. **Complete prototype and reference:** obtain lab review of the pack/charger harness, then connect the fused pack. Use the production firmware with its hardware lock still enabled. Establish actual full charge using the pack and matched charger documentation before holding the FULL button under the documented near-zero-current conditions. The diagnostic build ignores this button's command; a bench-supply voltage alone does not establish a full battery reference.
8. **Controlled switching:** after the above checks, apply reviewed calibration and set `HARDWARE_CONFIRMED=true` in the production build. Rebuilding/rebooting loses the charge reference; establish it again only after the documented physical full-charge procedure. Use a small power-only load before the fan; test RESTORE, local OFF, reset and sensor-fault shutdown. Validate actual fan startup current. Validate runtime with measured discharge trials; do not use BMS emergency cutoff as the ordinary endpoint.
9. **Thermal run:** measure shunts, Q1, terminals, fuses and converter after at least 30 minutes at the intended maximum load. Record ambient temperature, steady current, startup peak and component temperatures. Reduce the operating envelope or revise the design if the selected components' derated limits are not met.
10. **Solar:** connect only a matched controller's battery output to J2, then follow its required battery/panel connection sequence. Test charge-current polarity. Do not improvise controller grounding or use an undocumented LOAD terminal.

## Firmware and USB settings

The existing firmware matches the board's addresses, shunts and GPIO assignments. Keep `HARDWARE_CONFIRMED=false` until the checks above pass. Keep `SOLAR_SENSOR_FITTED=false` when J2 is connected to an ordinary mains charger; U3 then is physically present but its power is not labelled as solar. Set it true only for solar-controller operation, and rebuild.

For USB development: ESP32 powered from USB, J7 connected, JP1 **open**, J11 unconnected. Laptop-supplied ESP32 energy is then excluded from battery-energy measurements.

For independent battery operation: USB disconnected, JP1 fitted, J11 connected to the documented ESP32 5 V input and GND, J7 retained. Battery energy now includes the ESP32. For simultaneous logging, use a properly verified USB VBUS isolation arrangement; do not assume an arbitrary development board safely combines USB and external 5 V.

Use the same power arrangement for baseline and controlled-runtime comparisons. Document it in each test record.
