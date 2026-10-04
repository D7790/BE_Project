# Reference wiring and power design

Status: proposed laboratory reference. No physical assembly has been inspected. Use exact manufacturer terminal labels and ratings when turning this into the final schematic.

For the current four-layer revision B, follow `pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md` and its native KiCad schematic. If selecting the older two-layer A, use the guide in its own directory. The general power-flow principles below still apply, but PCB connector numbers, fuses, chip packages and jumper settings are defined in the matching assembly guide.

## Reference hardware

- Classic ESP32 development board, 3.3 V GPIO.
- Current PCB version: three INA219AIDR SOIC-8 ICs and 0.1-ohm shunts are on revision B. Breakout modules belong only to the separate module-based alternative.
- DS18B20 temperature sensor in powered three-wire mode.
- Assembled protected 4S LiFePO4 pack and its specified enclosed charger.
- 5 V DC converter with enough continuous and startup current for the chosen loads.
- Small 5 V lamp and fan, initially around 2.5 W / 0.5 A class, with measured branch current no more than 0.6 A each. Verify their allowed terminal voltage and fan startup demand. Constant-power 3 W loads can exceed 0.6 A after wiring/fuse drops; see `docs/HARDWARE_PERFORMANCE.md`. Keep the PCB's entire continuous 5 V load, including the ESP32 when supplied there, at or below 1.5 A (7.5 W).
- Active-high, 3.3 V-compatible load-switch driver or designed MOSFET circuit.

Read the board labels, not the position of a connector in an online photograph. Clone modules can have different layouts.

## Power connections

| Net / connection | Reference routing |
| --- | --- |
| Protected pack positive | Pack external positive -> suitable DC fuse near pack -> manual disconnect -> S1 IN+ |
| System junction positive | S1 IN- -> positive junction feeding charging connection and S2 IN+ |
| Load-branch positive | S2 IN- -> converter positive input |
| Protected system ground | Pack external protected negative -> converter negative, sensor GND and system signal ground |
| Regulated load rail | Converter 5 V output -> essential lamp and optional-load positive supply |
| Optional load return | Through the specified load-switch circuit, if a low-side design is used |
| Charger connection | Charger to protected system side so charge passes through S1; follow pack/charger port requirements |
| Optional solar measurement | Controller BAT+ -> S3 IN+ -> S3 IN- -> positive junction, subject to controller instructions |

All battery charging/discharge paths must pass through S1. Do not attach a charger directly on the battery side of the shunt if charge accounting is expected.

The BMS remains inside the purchased pack. Never join raw cell B- to system ground or bypass the BMS. If the purchased pack has separate charging/discharging ports, revise this common-port reference against its documentation.

Do not use the solar controller's LOAD terminals without reviewing whether its switching/ground arrangement is compatible with these measurement paths. For the first reference, the controller is used as a charger and the project has its own protected load branch.

S3 measures controller output at the battery connection, not panel-side power. Do not connect an INA219 directly to a panel whose worst-case open-circuit voltage exceeds its rating.

## ESP32 signal assignments

| ESP32 connection | Destination | Notes |
| --- | --- | --- |
| GPIO21 | INA219 SDA on S1/S2/optional S3 | Shared I2C bus |
| GPIO22 | INA219 SCL on S1/S2/optional S3 | Shared I2C bus |
| 3V3 | Sensor logic VCC and DS18B20 VDD | Verify modules work at 3.3 V |
| GND | Sensor grounds, DS18B20 GND, driver logic return | Protected system ground |
| GPIO4 | DS18B20 data | Approximately 4.7 kΩ pull-up to 3.3 V for this short-wire reference |
| GPIO25 | Active-high optional-load driver input | Must have a hardware pulldown so boot/reset leaves output off |
| GPIO27 | Momentary control button | Button to GND; firmware enables internal pull-up |
| GPIO26 | Separate full-reference confirmation button | Hold 5 s only after a verified full-charge procedure; button to GND |

Do not power a load or relay coil from a GPIO. A relay module's supply voltage and logic threshold are separate requirements.

Reference I2C addresses: S1 0x40, S2 0x41, S3 0x44. Follow the actual board's address-jumper instructions. Check installed pull-ups so multiple boards do not create excessive pull-up strength; every I2C pull-up must remain compatible with 3.3 V GPIO.

## Current measurement

S1 IN+ faces the battery and IN- faces the system. Positive battery current means discharge; negative means charge.

The firmware adds signed shunt drop to the INA219 bus voltage to estimate the battery-side terminal voltage. It applies per-channel current gain/offset values in firmware/include/config.h.

With a 0.1-ohm shunt, the ideal drop at 1 A is 0.1 V and dissipation is 0.1 W. At 2 A these become 0.2 V and 0.4 W. Board thermal limits, connector ratings and the actual shunt rating must support the intended operating current. These calculations do not certify a clone module.

Check both steady load and startup peaks. The firmware's configured 2 A limit is not a hardware current limiter.

## Optional-load driver

Revision B already includes the AO3400A driver, gate pulldown and SS14 diode. No extra driver module is needed. A separate module-based prototype would need a documented driver compatible with 3.3 V logic and the actual DC load.

If designing the discrete circuit, select the switching device using its on-resistance at the actual gate drive voltage, current/thermal requirements and load behavior. Threshold voltage alone does not establish that a MOSFET is fully on at 3.3 V. Include a gate/input pulldown, suitable drive components and transient suppression appropriate to the fan/coil.

A low-side switched load must not have another signal/data/ground connection that bypasses the switch. Use standalone power-only demonstration loads. Any USB load connection must be assessed for backfeed paths.

The initial scope switches only the optional branch. Stop physical discharge trials at the agreed normal reserve endpoint; do not depend on repeatedly triggering the BMS's emergency cutoff.

## Powering the ESP32 and connecting USB

During first bring-up, power the ESP32 from USB only, and do not also connect the converter's 5 V output to its 5 V/VIN pin. Sensor and driver grounds still follow the checked common-reference arrangement.

In this arrangement, battery/load measurements exclude energy provided by the laptop to the ESP32. The hardware dashboard therefore labels S2 as load-branch input, not a complete measurement of every external power source.

For the final self-powered system, supply the board from the battery converter through its documented input and arrange USB data/power isolation according to the exact development-board schematic. Do not assume an arbitrary board safely accepts simultaneous external 5 V and USB VBUS. Document which equipment draws battery energy during every comparison experiment.

Review grounded lab supplies, USB-connected computers and any oscilloscope earth connections before connection. Never use an earth clip to create an unintended return path around protection.

## Bring-up order

1. Identify and photograph the exact parts, markings and pinouts.
2. Check unpowered wiring, polarity, shorts, fuses and current-path ratings.
3. Verify the converter on a current-limited bench supply with the ESP32 disconnected.
4. Power the ESP32 and confirm sensors at the intended I2C addresses.
5. Compare voltage/current measurements at several known loads; verify sign.
6. Verify that the optional driver is off at reset, boot and sensor failure.
7. Add the battery only after the lab supervisor checks the assembly.
8. Establish a documented full-charge reference and a capacity basis before reserve subtraction, as defined in `docs/TEST_PLAN.md` from the project root. Do not use partial capacity measured only to the 20% reserve as total capacity.
9. Enable control in config.h only after the preceding checks.
10. Integrate the solar charger after battery-only behavior is stable.

## Primary references

- [Adafruit INA219 wiring](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/wiring)
- [Adafruit INA219 current and shunt limits](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/overview)
- [PlatformIO ESP32 reference target](https://docs.platformio.org/en/stable/boards/espressif32/esp32dev.html)
- [Espressif hardware design guidelines](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32/index.html)
