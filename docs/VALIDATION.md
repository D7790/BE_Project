# Implementation validation

Updated: 28 September 2026. The latest complete audit is in `FINAL_AUDIT.md`, and the execution checklist is `NEXT_STEPS.md`. Earlier findings remain in `CROSSCHECK_REPORT.md`. Browser visual checks below are retained from the earlier reviews; no new visual browser session is claimed by this final audit.

Current four-layer revision B passes ERC, DRC, connectivity/plane, component/footprint/BOM/interface, 20 explicit power-path and fabrication-export checks. The full simulation suite includes **45 Python tests and 67 host C++ assertions** (43 controller-policy, 24 checked-register-reader), nine original reduced SPICE circuits, six additional startup scenarios and accelerated ideal/nonideal plant/fault runs. Some modeled configurations deliberately fail voltage/rise-time screens. A passing suite detects those failures as intended. See `HARDWARE_PERFORMANCE.md` and `simulations/results/suite-summary.json` from the root for scope, results and current source hashes.

## Completed software checks

- The current 45 automated Python tests cover estimator arithmetic, faults, control transitions, malformed serial recovery, protocol consistency, local interfaces, calibration safeguards and electrical-model equations/power conservation. The current execution result is recorded in `simulations/results/suite-summary.json` from the project root.
- Host policy tests now include one-hour 10 Hz runs at 5 mA, 100 mA and 500 mA; these caught and verified the fix for accumulator precision loss.
- The C++ register-reader checks cover signs/scales, each transaction-failure position, configuration/calibration mismatch, overflow and sensor resets. They use a fake register source, not an electrical I2C emulator.
- The calibration CLI's four-channel synthetic example passed with its simulated label retained; no constants were applied to production firmware. Blank measurement fields remain blank in the lab template.
- JavaScript syntax checked with node --check web/app.js.
- Dashboard loaded from an isolated local review server in the Codex in-app browser; no captured console errors/warnings. The unavailable browser-harness connection did not prevent this check.
- Normal measurements, limited-backup load shedding, refused restoration and sensor-fault unknown estimates were observed through the interface.
- Solar scenario showed negative battery current and a charging state.
- Viewport checks at 1536, 390 and 320 CSS pixels found no horizontal page overflow. Desktop and 390-pixel layouts were visually inspected.
- Tests verified CSV provenance, preservation of negative charging current, rejection of malformed telemetry, stale-data detection and refusal of simulator commands in hardware mode.
- Tests verified cross-origin command rejection and that CSV text fields cannot become spreadsheet formulas.

The test fixtures and browser scenarios are synthetic. They are not battery measurements.

## Firmware build

The ESP32 firmware compiled successfully with the pinned PlatformIO configuration (espressif32 6.10.0, esp32dev). Build output: firmware/.pio/build/esp32dev/firmware.bin.

- RAM: 22,164 of 327,680 bytes (6.8%).
- Flash: 323,053 of 1,310,720 bytes (24.6%).
- Separate `bringup` target compiled: RAM 21,960 bytes; flash 303,189 bytes (23.1%). It provides raw diagnostics and holds GPIO25 low.
- Earlier clean builds emitted two nonfatal upstream OneWire warnings; the latest two incremental builds completed successfully.

An initial Windows compiler-launch failure was resolved by using the short tool-cache junction configured by build_firmware.ps1. No board was flashed, and compilation does not verify behavior on physical hardware.

## Not validated physically

- Sensor calibration and measurement accuracy.
- Pack capacity, charge-reference procedure or runtime error.
- Actual load-driver switching, reset behavior or thermal performance.
- Solar charger compatibility, charging behavior or energy-flow accuracy.
- Battery protection, any cell-level behavior or long-duration reliability.
- Any PCB footprint, fabricated board or assembled circuit.

The firmware defaults to physical control disabled. Confirm hardware and configuration before enabling it. A successful software test or compilation does not establish physical safety or measurement accuracy.
