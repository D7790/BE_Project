# Wattsense simulation and four-layer revision report

Date: 28 September 2026. **All numerical results here are simulated or software/CAD checks. No assembled hardware was tested.**

**Later extension:** [Hardware-performance modeling](HARDWARE_PERFORMANCE.md) adds actual copper path geometry, assumed electrical losses, six startup circuits and 18 paired runtime scenarios; the full suite now contains 45 Python tests. The 37-test table and 3 W ideal-load figures below document the earlier checkpoint. [Project flow](PROJECT_FLOW.md) explains how the physical system will operate. Do not mix load assumptions when comparing reports.

The current custom-board candidate is `hardware/pcb/wattsense-main-revB-4layer/`. Revision A remains in its original directory as a two-layer budget alternative. Do not mix their BOMs or manufacturing files.

## What was checked

| Check | Result | What it establishes |
| --- | --- | --- |
| Python regression suite | 37 tests passed | Estimation, policy, faults, malformed serial recovery, server and calibration fitting/validation in software |
| Production C++ controller on PC | 43 assertions passed: 16 locked, 27 armed-copy | Actual controller-header behavior, including one-hour 10 Hz precision checks; not ESP32 peripheral/timing emulation |
| INA219 checked register reader on PC | 24 assertions passed | Signed decoding, transaction failure, configuration/calibration mismatch, reset and overflow rejection with fake registers |
| ESP32 production build | Successful; RAM 22,164 B, flash 323,053 B | Firmware compiles for the pinned esp32dev target; no flashing performed |
| ESP32 diagnostic build | Successful; RAM 21,960 B, flash 303,189 B | Separate bringup target compiles; GPIO25 held low by its code; no hardware test |
| ngspice 46 reduced circuits | Nine circuit runs, including one deliberately exposed Rev A limitation | Selected DC, switching and RC behavior under stated assumptions |
| Accelerated battery/load plant | Baseline/priority pair plus nine capacity/efficiency pairs | Illustrative essential-load runtime tradeoff |
| Fault injections | Seven cases switched optional output off | Software response to disconnect, temperature, voltage, current, integration gap and NaN input |
| KiCad 10.0.6 ERC/DRC | Zero reported violations, zero unrouted items, zero parity issues | Configured schematic/geometric consistency |
| Independent PCB audits | 114 pad assignments matched; both inner GND layers single connected polygons; 20 explicit power paths checked | Pin mapping, component/footprint/BOM and firmware interface consistency; stated track-width continuity |

Machine-readable summaries, raw CSVs and logs are in `simulations/results/`. `suite-summary.json` records source hashes. PCB reports and checked native-source hashes are in the revision B `reports/` directory.

The latest run follows the purchasing-code change to INA219AIDR in revision B and a new audit of PCB/schematic/BOM values. Geometry and circuitry are unchanged by this carrier-code correction. The firmware now rejects a sample when any required INA219 transaction fails and checks configuration/calibration both before and after data reads. This does not establish coherent sampling under fast transients or emulate a physical I2C peripheral.

The calibration tool uses separate fit and held-out readings; nine Python tests cover offset convention, voltage gain, holdout failure, invalid/degenerate input, polarity, simulation labelling, distinct validation settings and prevention of raw-input overwrite. Its example CSV/report are deliberately synthetic. Follow `LAB_START_GUIDE.md` for actual calibration and remeasurement.

The cross-check exposed rounding loss in the C++ float state-of-charge accumulator at the actual 10 Hz cadence. Double-precision accumulation now passes one-hour tests at 5 mA, 100 mA and 500 mA. The Python ideal plant already uses double precision; its runtime figures therefore do not change. See `CROSSCHECK_REPORT.md` for all review findings and limits.

## Four-layer design

| Layer | Purpose |
| --- | --- |
| F.Cu | Components, power paths, analog sense and other routing, GND pour |
| In1.Cu | Continuous GND plane; no routed signal/power tracks |
| In2.Cu | Continuous GND plane; no routed signal/power tracks |
| B.Cu | Remaining signal routing and GND pour |

The board remains 100 x 90 mm, nominal 1.6 mm FR4, with 1 oz outer copper and 0.5 oz inner copper. There are 104 through vias, including 57 new ground-stitching vias. Each internal ground fill is approximately 8,529 mm² and forms one polygon. There are no blind/buried vias or microvias. The fabricator's actual symmetric stackup must still be confirmed; CAD dielectric dimensions are nominal.

These layers provide a continuous reference under outer routing and more ground connections. No measured reduction in noise, temperature or emissions is claimed. **The limits remain 2 A on the battery path and 1.5 A total continuous on 5 V.** Extra layers do not increase the ratings of fuses, shunts, connectors or components. Four layers are optional for this project; their delivered cost is unquoted, so the below-INR-10,000 total is not yet confirmed.

## Circuit simulation results

The reduced netlists are checked against revision B's audited source hashes and the relevant component values/pin connections. They are not a complete simulation of the native schematic.

### Shunt paths

The DC sweep contains 27 combinations: load current from 0 to 2 A in 0.25 A steps and charger current of 0, 1 or 2 A. The ideal battery holds 12.8 V. R1, R2 and R3 match the three 0.1-ohm shunts and their schematic connections.

- Battery current follows load current minus charger current, with the expected signed voltage across R1.
- At 2 A, one shunt drops 0.200 V and dissipates 0.400 W.
- Battery-to-converter current crosses two shunts: total 0.400 V drop and 0.800 W dissipation at 2 A, before wire/connector/trace losses.
- Numerical agreement with independent Ohm's-law/KCL expectations was within 3e-14 for the checked values.

The sweep does not establish resistor temperature or protection behavior. Fuse clearing, battery impedance, charger control and copper losses are not included.

### I2C pull-ups: an actual design correction

| Pull-up | Total assumed bus capacitance | Simulated 30%-70% rise | 100 kHz standard-mode 1 us limit |
| --- | ---: | ---: | --- |
| Rev A: 4.7 kOhm | 100 pF | 398 ns | Pass |
| Rev A: 4.7 kOhm | 200 pF | 796 ns | Pass |
| Rev A: 4.7 kOhm | 400 pF | 1,593 ns | Outside envelope |
| Rev B: 2.2 kOhm | 100 pF | 186 ns | Pass |
| Rev B: 2.2 kOhm | 200 pF | 373 ns | Pass |
| Rev B: 2.2 kOhm | 400 pF | 746 ns | Pass |

R4/R5 were changed to 2.2 kOhm in the schematic, PCB and BOM. R6 stays 4.7 kOhm. The formula tr = 0.8473 RC independently agrees with the simulated rise times. At 3.3 V, the ideal sink current with 2.2 kOhm is 1.5 mA per asserted line. The basis is [TI SLVA689, I2C Bus Pullup Resistor Calculation](https://www.ti.com/lit/an/slva689/slva689.pdf) and the [INA219 electrical specifications](https://www.ti.com/lit/ds/symlink/ina219.pdf).

This does not prescribe an arbitrary cable length. The final cable, parasitics and any parallel pull-ups must be checked on an oscilloscope. The 400 pF result is for the stated model, not a measurement of this PCB.

### Fan switch and high-impedance reset

The illustrative transient uses a 5 V source, an 8.333-ohm/1 mH load, a 48-milliohm voltage-controlled switch, assumed 1 nF gate capacitance, 330-ohm gate resistor and 47-kilohm pulldown. The diode uses an explicitly generic SPICE model.

| Quantity | Model result |
| --- | ---: |
| Gate high level | 3.278 V |
| Steady load current | 0.597 A |
| Switch conduction loss using fixed 48 mOhm | 17.1 mW |
| Peak drain voltage with generic flyback diode | 5.394 V |
| Gate below 0.5 V after GPIO becomes high impedance, assumed 1 nF | 88.4 us |

The on-resistance reference comes from the [AO3400A datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf). **This is not its vendor transistor model or a real BLDC fan model.** It does not predict Miller behavior, wiring spikes, actual startup/stall current, diode heating or junction temperature. A stuck-high GPIO is also different from high impedance. Measure the real circuit before relying on these values.

## System-level runtime comparison

The model uses an ideal fixed 12.8 V, 6 Ah battery initially at 68% charge, stopping at a 20% true operating reserve. Loads are a 3 W lamp, 3 W optional fan and 0.8 W controller behind a fixed 90%-efficient converter. There is no solar, ageing, temperature dependence or capacity uncertainty in this comparison. Initial usable energy is 36.864 Wh.

| Mode | Time to true reserve | Fan service |
| --- | ---: | --- |
| All loads retained | 4.879 h | Until reserve |
| Priority controller | 7.247 h | Shed at 1.880 h |

The resulting **48.53% longer essential-load service is a model result only**. It comes from removing the fan's consumption; it is not increased battery capacity, an efficiency improvement, or an equal-service comparison. The 3 h backup setting is a shedding trigger, not a guaranteed actual runtime. Nine further pairs covering 4/6/8 Ah and 80/90/95% converter efficiency showed longer lamp service under the same idealized assumptions.

The separate error example uses a true 4.8 Ah battery while the estimator assumes 6 Ah, with 0.50 A actual current measured as 0.52 A. After four hours, estimated charge is 45.33% versus 38.33% true charge: an overestimate of **7.00 percentage points**. This demonstrates why capacity measurement and current-offset calibration are required.

## Defects found and corrected

1. The Python model lacked the firmware's operating-voltage limits and accepted current slightly above the 2 A design ceiling. Their boundaries now agree.
2. Invalid or nonfinite restore inputs could pass comparisons. Restore now rejects them; the C++ controller also validates samples at its own boundary.
3. Temperature/voltage interruptions could leave partial shedding-timer history. Those interruptions now reset the timer.
4. Thirty 0.1-second float samples could sum just below 3 seconds in C++, delaying shedding by one sample. A 10 us comparison tolerance handles rounding; the host test checks the actual threshold.

## Use for Review 3 and next steps

Open `runtime-comparison.png`, `i2c-pullup-comparison.png` and `fan-transient.png` from `simulations/results/`. SVG versions are also available for slides. Show the circuit assumptions, the original pull-up limitation, the resulting CAD change and the rerun checks. Label every chart **simulation**.

Next physical steps: obtain delivered quotes, verify exact parts/footprints and pack/charger wiring, assemble and bring up on a current-limited bench supply, measure I2C waveform and fan startup, calibrate all sensors, check temperature/voltage drop and then run a logged baseline-versus-control experiment. Battery/BMS behavior, charger regulation, actual capacity, faults, thermal limits, EMC and reliability remain unvalidated.

## Reproduce

Run `run_simulations.ps1` from the project root. See `simulations/README.md` for installed runtimes and model scope. The [ngspice shared-library interface](https://ngspice.sourceforge.io/shared.html) is used locally through KiCad's bundled DLL. Production firmware remains `HARDWARE_CONFIRMED=false`; the armed host test is an isolated temporary copy.

Run the revision B `check_and_export.ps1` after any CAD edit. It performs ERC, DRC/parity, netlist export, independent connectivity/plane checks and fabrication packaging. Old simulation/CAD results do not validate changed sources.
