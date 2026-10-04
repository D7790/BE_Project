# Wattsense

Battery-mounted, battery-powered monitoring and advice using remaining-energy/runtime estimates and known AC/DC load signatures.

**Current scope — clarified 3 October 2026:** Start with [the battery-centred scope](docs/BATTERY_CENTRED_SCOPE.md). WattSense mounts near the battery and runs from a regulated battery supply. It estimates remaining charge, usable energy and runtime, then recommends which optional loads to turn off using known signatures and user priorities. Solar or a compatible AC-to-DC charger charges the battery; DC loads use converters and AC loads use an inverter. Random Forest is a candidate to compare with a Decision Tree and feature baseline; no measured signatures or classifier accuracy exist yet.

**Current Review 3 presentation:** [Editable 14-slide battery-centred deck](output/pptx/WattSense_Review_3_Battery_Centred_Final.pptx). It presents the battery-powered monitor/adviser, AC/DC load paths, charging options, confirmed team details and 20 literature titles. It supersedes the standalone AC-first scope.

**Existing foundation:** The [30 September project and paper audit](docs/RECHECK_2026-09-30.md) records checks of the small DC implementation. The [earlier buying/build checklist](docs/NEXT_STEPS.md), research paper and team guides describe that narrower scope. The [paper guide](paper/READ_ME_FIRST.md) links the retained PDF and editable Word companion; these documents need follow-up narrative alignment before reuse for the expanded project.

This folder now contains a runnable local dashboard, a development simulator, a USB-serial collector, timestamped CSV logging, ESP32 firmware, automated software tests and hardware implementation notes.

**DC foundation PCB:** `hardware/pcb/wattsense-main-revB-4layer/` contains revision B: a routed four-layer KiCad board with two internal ground planes, updated I2C pull-ups, prototype fabrication exports, BOM and assembly guide. Its 2 A battery-side and 1.5 A continuous 5 V project ceilings need physical qualification. It cannot connect to mains or carry household-inverter battery current. The original two-layer revision A remains in `hardware/pcb/wattsense-main/` as a historical alternative. Do not mix their BOMs/exports. Physical assembly and delivered pricing remain pending.

**DC foundation simulation results:** `docs/SIMULATION_REPORT.md` contains the 28 September tests, reduced SPICE results, runtime comparison and limitations. Run `run_simulations.ps1` to reproduce the suite; figures and raw data are in `simulations/results/`. They do not validate the proposed AC measurement or signature stage.

**Retained DC hardware-performance models:** [Results, startup limitations and smaller starter loads](docs/HARDWARE_PERFORMANCE.md), plus [the earlier DC flow](docs/PROJECT_FLOW.md), include actual PCB path geometry, assumed electrical losses, 18 paired runtime scenarios and six additional ngspice startup cases. With the stated 2.5 W starter loads, the model predicts 5.48 h versus 7.88 h of lamp service; these are simulated DC results. The recorded full suite contains 45 Python tests and 67 C++ assertions.

**Next practical steps:** Qualify battery-powered monitoring, complete the needed data path and collect known-load profiles using [the battery-centred plan](docs/BATTERY_CENTRED_SCOPE.md). Larger inverter setups need whole-battery sensing rated for their current; the 2 A Rev B path is unsuitable. The below-₹10,000 target is unchanged; the earlier ₹9,700 DC allocation excludes added inverter/AC equipment, so delivered affordability needs a complete quote or borrowing plan. The [Pune buying plan](hardware/BUYING_PLAN_PUNE.md), [supplier questions](hardware/SUPPLIER_QUESTIONS.md) and [first lab session](docs/LAB_START_GUIDE.md) remain DC foundation resources. A separate `bringup` firmware build keeps the fan off while reporting raw sensors. The `calibration/` folder contains a blank lab worksheet and explicitly simulated examples; no real measurements have been recorded.

**Earlier cross-check completed:** [Review findings and remaining physical tests](docs/CROSSCHECK_REPORT.md). Corrected 10 Hz firmware accumulation precision, malformed serial handling, calibration safeguards and conflicting lab instructions. That checkpoint passed 37 Python tests, 67 native C++ assertions, both ESP32 builds and refreshed CAD audits. The newer hardware model adds eight Python tests; native CAD is unchanged.

**There is no physical prototype yet. Simulator values are illustrative and must not be presented as experimental results. The firmware's physical output is disabled by default.**

## Start the DC foundation demonstration

This runnable demo illustrates the existing battery/runtime and priority-control foundation. Household AC measurement and signature recognition are planned additions and are not demonstrated by it.

From this project folder in PowerShell:

    .\.venv\Scripts\python.exe -m wattsense.server --mode simulated

Open http://127.0.0.1:8765 in a browser. If it is already running, just open that address. You can also run run_demo.ps1 or double-click run_demo.cmd.

Press Ctrl+C to stop a terminal-launched server. The background demo started during project setup can be stopped with stop_demo.ps1; the script checks the recorded process identity before stopping it. CSV records are flushed throughout the session.

The simulator needs only Python 3.10 or newer. On another computer without the supplied local environment:

    python -m wattsense.server --mode simulated

The server listens only on this computer. No cloud service, account or API key is required.

### Try these actions

1. Normal load: view the illustrative charge, power and runtime.
2. Limited backup: wait about four seconds and observe the optional load switch off.
3. Restore fan: the controller refuses restoration when the predicted full-load runtime is too short.
4. Solar charging: battery current becomes negative. The no-future-charge runtime heuristic excludes future solar input.
5. Sensor disconnected: charge/runtime become unknown and the optional load switches off.
6. Export session CSV: save the data with its simulated/hardware source label.

Resetting a scenario establishes a new simulated reference and clears the visible chart. The full session CSV retains earlier records; scenario resets appear as device-uptime discontinuities and are documented in the on-screen event log. The simulator uses real elapsed time, not accelerated battery discharge.

## Use physical hardware later

Read hardware/REFERENCE_WIRING.md and firmware/README.md before connecting a battery.

Create/install dependencies if needed:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m wattsense.server --list-ports

Start hardware mode with the actual serial port:

    .\.venv\Scripts\python.exe -m wattsense.server --mode hardware --serial-port COM5

COM5 is an example. Hardware mode does not fall back to simulated data when a sensor or serial connection is missing. The dashboard is read-only in hardware mode. The ESP32 handles physical load decisions independently of the computer.

Close the dashboard's hardware server before opening the same port in a serial terminal or uploading firmware. Opening an ESP32 serial connection can reset the board; charge starts unknown after each reboot.

## Build firmware

    .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
    .\build_firmware.ps1

build_firmware.ps1 runs the build using the project environment. It creates a short Windows junction at your user profile's .ws-pio pointing to this project's .local/platformio cache. This avoids compiler process/path failures in the longer workspace path; package files stay in the project. The script refuses to overwrite an unrelated path. Building does not flash a board.

The reference target is a classic ESP32 development board with GPIO21/22 available for I2C, not an ESP32-C3/S3 board. Exact module and board compatibility must be checked before wiring or uploading. GPIO27 provides local load control, and a separate GPIO26 button permits full-reference confirmation while the dashboard remains connected.

## Run software tests

    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Tests cover the reference estimator, charge/discharge sign, reserve handling, measurement gaps, load restoration, simulator scenarios, serial message validation, logging and the HTTP interface. Software tests do not establish physical battery accuracy.

## Folder map

| Path | Purpose |
| --- | --- |
| docs/BATTERY_CENTRED_SCOPE.md | Current battery-powered monitor/adviser scope, AC/DC loads, charging and development plan |
| docs/EXPANDED_SCOPE_AC_DC.md | Superseded standalone AC-first plan; retained for history |
| wattsense/model.py | Simulator reference estimator and control policy |
| wattsense/simulator.py | Illustrative battery/load/solar model |
| wattsense/server.py | Local server, serial collector and CSV recorder |
| web/ | Dashboard interface, with no external assets or CDN dependency |
| firmware/ | PlatformIO ESP32 firmware and configuration |
| hardware/REFERENCE_WIRING.md | Power paths, signal assignments and assembly checks |
| hardware/BOM.md | Buying specification and provisional budget |
| hardware/PCB_REQUIREMENTS.md | PCB design status and physical validation criteria |
| hardware/pcb/wattsense-main-revB-4layer/ | Current four-layer revision B, KiCad sources, prototype fabrication files and checks |
| hardware/pcb/wattsense-main/ | Preserved two-layer revision A budget alternative |
| simulations/ | Reproducible SPICE, host C++ tests, plant runs and figures |
| docs/REVIEW_DEMO.md | Review demonstration and completed/pending claims |
| docs/TEST_PLAN.md | Physical validation procedures and blank results tables |
| docs/PROTOCOL.md | Serial telemetry format and sign conventions |
| tests/ | Automated software tests |
| logs/ | Local CSV session recordings, ignored by Git |
| WATTSENSE_PROJECT_BLUEPRINT.md | Historical DC foundation blueprint, superseded by the expanded roadmap |

## Current limitations

- Hardware has not been assembled, calibrated or tested.
- The final battery-powered device, complete whole-battery sensing path and larger compatible backup setup remain to be qualified. Any supporting AC meter must use a documented isolated data interface and enclosed test arrangement.
- No measured appliance-signature dataset, raw AC logger, trained classifier or validated UNKNOWN rule exists yet. Random Forest is an initial candidate, not an achieved model result.
- The current INA219/DC board and serial protocol do not acquire AC real power, RMS values or power factor. A new meter adapter and data path are required.
- Known-load energy attribution, recommendation benefit and backup-runtime errors have not been evaluated. Aggregate load combinations are a later milestone; similar profiles may remain ambiguous.
- The historical ₹9,700 DC allocation excludes the added AC and household backup equipment; the expanded budget is unconfirmed.
- Pack capacity, efficiency and temperature/voltage limits are provisional.
- The retained DC firmware requires a verified manual charge reference; automatic full-charge detection is not implemented.
- Temperature is measured at the battery surface, not inside cells.
- The DC foundation's runtime uses remaining charge times nominal voltage, with a configured reserve. Its no-future-charge heuristic uses load-branch power and omits some upstream losses; it is not a guaranteed minimum runtime and requires evaluation against actual discharge runs. The household AC backup estimator is a planned separate extension.
- The DC simulator mirrors the existing priority policy; ESP32 firmware additionally checks its hardware lock and voltage limits. Tests of the Python model are not execution tests of the ESP32 binary.
- In the retained DC demonstrator, the essential load is not individually metered. Optional-load status reports the controller command; there is no independent relay-contact feedback. This is not an implemented household AC switching system.
- Appliance recognition is now part of the planned expanded scope. Cloud services and a mobile app are optional; no such integration is implemented. The retained DC CAD/fabrication files are engineering prototype designs awaiting physical validation.
- BMS and charger protections remain necessary. The ESP32 is not the pack's safety BMS.
