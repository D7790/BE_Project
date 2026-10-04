# Design notes and verification basis

## Architecture and boundaries

This board implements the project's measurement and priority-control contribution. The commercially assembled pack/BMS handles cell protection; a matched charger handles charge regulation; an external converter produces 5 V. There is no mains circuitry or cell balancing on the PCB.

R1 measures signed pack current, R2 measures the converter branch and R3 measures charger output. Each current-monitor supply is 3.3 V from the ESP32. The common return connects only to the protected external negative terminal of a compatible common-port pack.

This first revision uses fixed addresses and one optional load. Three current monitors permit a measured energy-flow balance. A fourth monitor or second load switch is not required for the selected academic scope.

## Pinout and package checks

The [TI INA219 datasheet, pin table and address table](https://www.ti.com/lit/ds/symlink/ina219.pdf) specifies **SOIC-8** pins: 1=A1, 2=A0, 3=SDA, 4=SCL, 5=VS, 6=GND, 7=IN-, 8=IN+. The DCN SOT-23-8 version has a different mapping. The board uses INA219AID and the SOIC-8 3.9 x 4.9 mm / 1.27 mm pitch footprint. These are ICs, not breakout modules.

| IC | A1 | A0 | Address | Measurement |
| --- | --- | --- | --- | --- |
| U1 | GND | GND | 0x40 | Pack, IN+ toward battery |
| U2 | GND | 3V3 | 0x41 | Converter input, IN+ toward system |
| U3 | 3V3 | GND | 0x44 | Charger output, IN+ toward charger |

The [AO3400A manufacturer datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) gives pin 1 gate, 2 source, 3 drain and a maximum 48 milliohm on-resistance at 2.5 V gate drive under its specified test conditions. A 3.3 V GPIO therefore has a documented low-voltage on-resistance basis. Do not substitute an IRF520-type module or select a MOSFET by threshold voltage alone.

Terminal block reference: [Phoenix Contact MKDS 1,5/2-5,08, 1715721](https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-15-2-508-1715721?type=pdf). Pin pitch is 5.08 mm, with the corresponding KiCad MKDS footprint. A cheap compatible substitute is acceptable only after checking its drill, body and wire-entry dimensions. MKDSN is a different housing family.

Fuses use the [Littelfuse 466 series, 1206](https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f), not the 0603 467 series. F1=0466002.NR, F2/F3=0466001.NR. Apply the manufacturer's normal continuous-current derating and additional temperature derating. Startup pulses must be checked against the actual time-current and I-squared-t characteristics.

## Calculations and design targets

### Current shunts

For a 0.1-ohm resistor, Vdrop = I x 0.1 and P = I-squared x 0.1:

| Current | Drop per shunt | Dissipation per shunt |
| ---: | ---: | ---: |
| 0.5 A | 50 mV | 25 mW |
| 1.0 A | 100 mV | 100 mW |
| 2.0 A | 200 mV | 400 mW |

The selected [Vishay WSL2512 family](https://www.vishay.com/docs/30100/wsl.pdf) provides a 1 W reference part, WSL2512R1000FEA, at the specified rating conditions. Operating at 2 A gives 0.4 W in each loaded shunt; this still requires checking temperature derating and solder-joint temperature on the actual board. Battery-to-load current passes through R1 and R2, so the combined shunt drop is twice the per-shunt value. Charger-to-battery current passes through R3 and R1.

The existing INA219 library calibration expects 0.1-ohm shunts. The 32 V register range does not permit 32 V at the IC: its specified input common-mode limit is 26 V. This project normally operates at or below 14.6 V, with a 2 A design ceiling and much smaller expected operating current. Calibration and actual capacity remain mandatory.

Sense traces originate on the shunt pads separately from the wide current tracks. These are two-terminal shunts with separate PCB sense takeoffs, not true four-terminal resistors. Residual pad/contact errors must be included in calibration.

### Fan switch

At 0.6 A, using the 48 milliohm room-temperature maximum reference gives I-squared x R = 0.0173 W in Q1. At a 1 A transient this is 0.048 W. On-resistance rises with temperature; these estimates do not include switching or abnormal conditions. The fan's startup/stall current and real package temperature must be measured.

The 330-ohm gate resistor limits an ideal initial 3.3 V step to about 10 mA. The 47-kilohm pulldown makes gate voltage about 3.28 V for a 3.3 V high and defaults it low when the GPIO floats. This circuit is intended for occasional on/off control, not a high-frequency motor PWM controller.

[Vishay SS14](https://www.vishay.com/docs/88746/ss12.pdf) is the flyback-diode family reference: cathode to FAN_P, anode to FAN_RETURN. Its current and thermal capability must suit the selected load. Use a two-wire, power-only demonstration fan. A third ground/data connection can bypass a low-side switch.

### Supply protection and decoupling

[SMBJ15A](https://www.vishay.com/docs/88392/smbj.pdf) is a unidirectional 15 V stand-off TVS on the battery-level system node, with cathode to SYS_P. It is a transient suppressor, not a voltage regulator, reverse-polarity blocker or substitute for the external fuse. A fault-capable source must have coordinated protection. The design does not claim compliance with surge/EMC standards.

Each INA219 has a local 100 nF supply bypass and a 10 nF differential-input capacitor. R4/R5 provide one pair of 4.7-kilohm I2C pull-ups to 3.3 V. R6 is the 4.7-kilohm 1-Wire pull-up. R9/R10 and C6/C7 give approximately 1 ms RC filtering on the external buttons. Firmware still handles button timing.

C11 is 47 uF / 25 V on the 5 V rail with a 5 mm radial body and 2 mm lead pitch. It is local bulk decoupling, not a replacement for the external converter's stability network.

### Copper and fabrication

- Two copper layers, 1 oz finished outer copper target, 1.6 mm FR-4.
- Main supply paths: 1.5 mm tracks; fan return 1.2 mm with a short 0.65 mm approach to Q1 drain; source approach 0.6 mm plus ground pours.
- Signal traces: 0.25 mm; small supply/ground connections: 0.35 mm.
- Copper clearance: at least 0.20 mm; zones 0.25 mm; board-edge copper clearance at least 0.5 mm.
- Signal vias: 0.7 mm diameter / 0.35 mm finished drill. No blind/buried vias or controlled-impedance requirement. No intentional via-in-pad.
- Ground planes on both layers, with explicit wide current-return tracks and direct pad connections. Directly connected ground pads need adequate soldering heat.
- Main power routes stay on the top layer. Ground and signal vias provide interlayer connections; no high-current path relies on a single signal via.

Track width is a design choice for this low-current prototype, not a verified temperature-rise result. Measure temperature and voltage drop on the assembled PCB. Use the fabrication stackup actually quoted by the supplier; any change in copper weight, outline, connectors or operating current requires review.

## What the checks establish

ERC checks schematic connectivity and pin-rule consistency. PCB DRC checks geometric rules, shorts, unrouted items and schematic parity. The independent audit additionally checks every schematic/PCB/manifest pin-net assignment and the critical INA219, MOSFET, diode and connector mappings. These do not establish actual component authenticity, mounting fit of substitutes, firmware runtime behaviour, sensor accuracy or battery-system reliability.

All acceptance measurements remain blank until the team records physical evidence. Successful compilation and clean CAD checks are not measured experimental results.
