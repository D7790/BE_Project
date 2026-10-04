# Wattsense: first lab session and calibration

Prepared 28 September 2026 for the four-person team. No hardware has been purchased, connected or tested. Current board: revision B, four layers. Start with the college supply and meter; the battery is needed later for charge and runtime experiments.

## What to do first

1. Obtain the small starter items in `hardware/BUYING_PLAN_PUNE.md`. Confirm the classic ESP32 exposes GPIO4/21/22/25/26/27. Build the diagnostic firmware now; upload only after the actual board and COM port are checked.
2. Prepare the PCB component order from revision B's `BOM-grouped.csv`. Three INA219 ICs and their shunts are on the custom PCB. Do not also buy three INA219 breakout modules unless deliberately choosing a temporary module prototype.
3. Assemble and inspect using `hardware/pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md`. That file contains the authoritative connector map, polarity and staged power procedure.

One team member handles assembly/wiring, one firmware and serial evidence, one independent meter readings, and one records test conditions and results. Have the lab supervisor review the battery/charger harness before battery operation.

## Dedicated diagnostic firmware

From a PowerShell terminal in the project root:

```powershell
.\build_firmware.ps1 -Environment bringup
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE '.ws-pio'
.\.venv\Scripts\python.exe -m platformio device list
```

After selecting the physical board, replace the example `COM5` below with its actual port:

```powershell
.\.venv\Scripts\python.exe -m platformio run --project-dir firmware --environment bringup --target upload --upload-port COM5
.\.venv\Scripts\python.exe -m platformio device monitor --port COM5 --baud 115200
```

Close the dashboard/other serial programs before opening the port. The diagnostic build holds GPIO25 LOW, ignores incoming serial commands and cannot enable the fan. Its startup configures the sensor registers; it does not modify firmware calibration constants or establish a charge estimate. `HARDWARE_CONFIRMED` does not arm this build. The hardware pulldown must still be checked during reset, before firmware runs.

On boot, `type: bringup_scan` reports I2C addresses in decimal. Expect **64, 65, 68**, corresponding to **0x40, 0x41, 0x44**. With only an ESP32 connected, an empty scan is expected; that does not validate the PCB.

Once per second, `type: bringup` reports:

| Field | Meaning |
| --- | --- |
| source_mode | `hardware_diagnostic`; distinct from dashboard telemetry |
| optional_output_commanded_on | Always false in this build; this is a command state, not measured fan feedback |
| load_button_pressed / full_button_pressed | Physical input states only; no actions are performed |
| temperature_c | Powered DS18B20 reading, or null for invalid/missing reading |
| sensors[].channel | battery, load or charger |
| sensors[].valid | Every required register transaction succeeded, expected configuration/calibration retained and overflow clear |
| raw_current_a | Signed, uncorrected INA219 current in amperes |
| raw_bus_v | IN- voltage relative to GND |
| raw_input_v | IN+ estimate = bus voltage + shunt voltage |
| raw_shunt_mv | Signed differential voltage across the shunt |

This output is **not** the normal dashboard protocol. A valid register reading alone does not prove correct wiring or accuracy. The reads are sequential and are not an atomic ADC snapshot; calibrate under steady conditions. All three ICs are inspected even when the production solar measurement flag is false.

## Power and measurement sequence

- Follow the board assembly guide's unpowered checks, logic-only stage, 5 V checks and default-off check first. JP1 stays open when the ESP32 is powered by USB. Keep the battery and charger disconnected during bench-supply tests.
- With the converter unloaded, start the battery-side bench supply at 12–13 V and a 100 mA limit. Increase deliberately as required for measured essential-branch loads. Do not exceed the 2 A battery-path ceiling or 1.5 A total continuous 5 V ceiling. Start with approximately 2.5 W / 0.5 A class lamp and fan, and measure no more than 0.6 A per branch. Qualify startup separately; `HARDWARE_PERFORMANCE.md` shows supply-drop counterexamples.
- Confirm the converter's actual 5.0 V output and current limiting before connecting J4. Marketing current ratings are not a thermal test.
- Use an independent meter. Voltage probes go across the stated nodes. Current measurements require the meter's fused current input **in series** with the relevant path; never put an ammeter across a source. Power down before rewiring it and restore the voltage socket afterwards.
- To obtain true zero-current points for U1/U2, use USB logic power, disconnect power sources and discharge capacitors; verify there is no current path. Then collect steady known loads. Positive battery current means discharge into the system.
- Charging-direction and U3 calibration come later, with a verified matched charger and protected pack. Do not connect a bench supply across a battery or reverse the pack to create negative calibration current. Do not reverse a unidirectional bench supply into a current-sinking arrangement.

## Record real calibration data

Copy `calibration/measurements-template.csv` to `calibration/my-measurements.csv`. The template intentionally has blank measurements and cannot pass as a result. Delete channel rows for channels not yet measured; an omitted channel remains uncalibrated. Use more points than the minimum when possible.

| CSV channel | Diagnostic raw field | Independent reference | Unit |
| --- | --- | --- | --- |
| battery_current | battery.raw_current_a | Series current in J1 path, discharge positive | A |
| load_current | load.raw_current_a | Series current in J3 converter input | A |
| solar_current | charger.raw_current_a | Series current entering J2, charger to system positive | A |
| battery_voltage | battery.raw_input_v | J1 pin 1 relative to J1 pin 2 | V |

The `solar_current` name matches the firmware constant; calibrating it with a matched mains charger does not make that energy solar. Leave `SOLAR_SENSOR_FITTED=false` until an actual solar controller is used.

For each current channel, record at least three distinct `fit` settings including zero and spanning at least 0.2 A. Then acquire at least two **new** `validation` settings. For battery voltage, record at least three fit settings spanning 1 V within the planned operating range and two new validation settings. Do not change a battery's voltage with a bench supply; voltage sweeps use a disconnected-battery bench setup. Use safe loads and independently observed references, not resistor nameplate estimates.

Keep notes beside the CSV: date, PCB revision, exact instruments and range, supply/load arrangement, averaging duration, ambient temperature and reference uncertainty. Use steady paired readings; temperature and switching transients are not calibration points. `source_mode=hardware` is a declaration by the operator, not proof of provenance.

```powershell
.\.venv\Scripts\python.exe -m wattsense.calibration calibration/my-measurements.csv --output calibration/my-report.json
```

The tool proposes `corrected_current = raw * gain - offset`, matching `config.h`, and a gain-only voltage correction. It checks fit and held-out readings against **±(3% of reference + 10 mA)** for current and **±1%** for voltage. These are project acceptance targets, not certified accuracy. Gross gain/offset corrections trigger review. It warns when battery-current validation does not cover both charge and discharge; passing discharge data alone must not be presented as bidirectional validation.

`CANDIDATE_PASS` means only that the supplied data meets these numerical checks. Inspect residuals, range, sign and instrument uncertainty, then manually enter approved constants in `firmware/include/config.h`. The tool never writes firmware. Rebuild and independently remeasure new points across the intended range; repeat after significant wiring/component changes.

For a dry run with deliberately synthetic data:

```powershell
.\.venv\Scripts\python.exe -m wattsense.calibration calibration/examples/simulated-measurements.csv --allow-simulated --output calibration/examples/simulated-report.json
```

Never copy the example constants into hardware configuration. The CLI refuses simulated data unless that flag is explicit, and rejects mixed hardware/simulation inputs.

## Move to the production experiment

Build with `.\build_firmware.ps1 -Environment esp32dev`. Use `--environment esp32dev` when uploading. The production build starts with an unknown charge reference on every reset and ships with `HARDWARE_CONFIRMED=false`.

After wiring, calibration, temperature, default-off behavior and the pack/charger arrangement pass lab review, enable the production hardware flag. Rebuild/upload and establish a reference in that boot session only after the documented actual full-charge procedure. A bench voltage or a simulated report does not establish battery charge. Follow `firmware/README.md` for the FULL button and permitted operating conditions.

Then test a small power-only optional load, the actual fan's startup, manual OFF/restore, reset and sensor disconnection. Finish with temperature measurements and matched baseline-versus-priority discharge trials using the same pack, starting charge, loads and controller power arrangement. Follow `TEST_PLAN.md` for `MIN_H 0` versus `MIN_H 3` and the independent stop endpoint. That file also defines capacity before reserve subtraction; partial Ah to the 20% reserve is not total capacity. Record essential-load service, fan service sacrificed, energy, temperature and estimation error. Those measurements are the final-year engineering evidence.

## Review 3 evidence

Show the four-layer CAD, its clean reports, the compiled firmware, clearly labelled simulations and this staged test plan. If parts arrive, add real serial/meter evidence with dates. PCB delivery to Pune 411048 is not confirmed; the review must not depend on an assumed delivery date. Keep unperformed hardware tests marked pending.
