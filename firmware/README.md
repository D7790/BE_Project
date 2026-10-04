# ESP32 firmware

Reference target: classic ESP32 development board, three INA219 ICs on the revision B PCB (battery, converter input and charger), powered DS18B20 and an active-high optional-load driver. The third measurement is optional in the production protocol; the diagnostic build inspects all three.

**This code has no physical validation yet. HARDWARE_CONFIRMED is false, so GPIO25 remains off. It is not battery-protection firmware.**

## Configuration

Review include/config.h against the exact hardware:

- Board/pin assignments and I2C addresses.
- INA219 shunt and current range.
- Current gain/zero-offset and battery voltage correction.
- Independently established full-to-normal-endpoint capacity, before reserve subtraction, and the operating reserve. See `../docs/TEST_PLAN.md`; partial Ah measured only to the 20% reserve must not be entered as total capacity.
- Pack-specific operating voltage and temperature constraints.
- Measured battery-side optional-load power increment.
- Actual driver polarity and reset behavior.

Do not switch HARDWARE_CONFIRMED to true until power wiring, fusing, sensor readings, temperature sensing, driver polarity and default-off behavior have been checked in the lab. The firmware assumes HIGH enables the optional load and LOW disables it. Active-low relay modules are not drop-in substitutes.

If there is no actual solar controller, SOLAR_SENSOR_FITTED remains false and solar_w is null, including when U3 is physically fitted and J2 uses a matched mains charger. The dashboard displays no solar measurement instead of inventing a zero reading.

## Build and upload

From the project root:

    .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
    .\build_firmware.ps1

After selecting and checking an actual board, upload with its port:

    $env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE '.ws-pio'
    .\.venv\Scripts\python.exe -m platformio run --project-dir firmware --environment esp32dev --target upload --upload-port COM5

COM5 is an example. No upload has been performed.

The build script uses a short junction to the project-local tool cache to work around Windows compiler path limitations. It does not move package files or overwrite an existing unrelated folder.

## First-power diagnostic build

Run `.\build_firmware.ps1 -Environment bringup` from the project root. When uploading it, select `--environment bringup`. It holds GPIO25 low, scans addresses 0x40/0x41/0x44 and prints raw current/voltage, temperature and button states at 115200 baud. It configures the INA219 registers but ignores all serial commands and cannot establish a charge reference or enable the fan. Its `hardware_diagnostic` records are separate from the production dashboard protocol.

Follow `../docs/LAB_START_GUIDE.md` for the staged lab procedure, serial fields and independent meter measurements. `../calibration/measurements-template.csv` and `python -m wattsense.calibration` provide a checked fit/holdout workflow. Calibration candidates are never applied automatically.

## Behavior

- Measurement loop nominally 10 Hz; telemetry nominally 1 Hz.
- Every INA219 register transaction used in a sample must succeed. The checked reader verifies configuration and calibration before/after data reads and rejects math overflow; it does not let a later successful transaction hide an earlier failure. Host tests inject transaction failures and register resets. These are sequential reads, not a latched simultaneous conversion; electrical bus timing remains a lab check.
- Signed current: positive = discharge, negative = charge.
- Charge starts unknown after every reset. No percentage is inferred from voltage alone.
- Missing/invalid measurements or an integration gap longer than 2 seconds invalidate the charge estimate and disable the optional load.
- A diagnostic charge checkpoint is written occasionally. It is not automatically trusted after reboot because energy used while the controller was off is unknown.
- Runtime is estimated to the configured reserve. The control policy uses a no-future-charge heuristic based on nominal remaining energy and measured load-branch power. Some upstream losses are omitted, so this is not a guaranteed minimum runtime.
- Shedding follows a sustained condition; restoration is explicit and checks predicted consumption with the optional load on.
- A physical button on GPIO27 toggles off or requests restoration. It cannot override lockout, invalid state or operating limits.
- A separate button on GPIO26 establishes the operator-confirmed full-charge reference when held for five seconds. The same measurement checks as the serial synchronization command apply.

The essential branch remains separately powered. There is no independent contact-state sensor, automatic charger control or cell-level monitoring.

## Local serial commands

Use a 115200-baud serial terminal with newline ending. Close the hardware dashboard server first so it releases the port.

| Command | Action |
| --- | --- |
| OFF | Immediately disables the optional output |
| RESTORE | Requests optional output; refused unless all conditions pass |
| MIN_H 3.0 | Sets the no-future-charge runtime threshold from 0 to 12 hours |
| SYNC_FULL_CONFIRMED | Operator confirms a verified full-charge reference |

Only issue SYNC_FULL_CONFIRMED after charging with the correct charger and confirming the pack's specified full-charge procedure, then arranging a valid measurement with near-zero battery current. The firmware additionally requires plausible voltage (13.4 V to configured maximum) and absolute battery current ≤0.10 A. Those checks do not independently prove the battery is full.

Acks are JSON objects with type "ack". They are not telemetry frames and are ignored by the collector.

The USB connection may reset an ESP32 when reopened. Connect the dashboard first, then establish the reference in the current boot session using the GPIO26 button after the verified full-charge procedure. This permits synchronization without closing the dashboard's serial connection. Label the button “FULL REFERENCE · HOLD 5 S” and explain that pressing it does not charge the pack.
