# Review 3 demonstration

Current execution plan: `NEXT_STEPS.md`; current audit: `FINAL_AUDIT.md`. The original SIH PPT is preserved, but its AI/NILM/cloud/BMS claims are not the implemented scope. Update those slides before presenting it as the current project. The review date must be confirmed by the team; the old five-day plan is not a fabrication delivery promise.

## What exists now

- Runnable local dashboard with a persistent simulated-data label.
- Illustrative battery, consumption and solar scenarios.
- Charge integration and reserve-aware runtime estimation.
- Sustained optional-load shedding and explicit restoration with margin.
- Sensor-fault behavior, event history and CSV export.
- USB-serial collector for the documented ESP32 protocol.
- ESP32 source, build configuration, wiring reference and purchasing specification.
- Automated tests of the reference model, protocol and local server.
- Four-layer revision B KiCad design, checked fabrication outputs and BOM, with revision A retained as a budget option.
- Reproducible reduced SPICE circuits and labelled runtime/RC/transient plots; see `SIMULATION_REPORT.md`.
- Nonideal electrical/runtime models with six additional startup cases and eighteen paired sensitivity scenarios; see `HARDWARE_PERFORMANCE.md`. The smaller 2.5 W starter-load case is separate from the older 3 W ideal comparison.

For a short engineering-design explanation, show `simulations/results/i2c-pullup-comparison.png`: the 4.7 kOhm / 400 pF model misses the rise-time limit, leading to the 2.2 kOhm change in revision B. Show the exact changed BOM and clean CAD checks. Describe this as a simulation-driven design decision, not a measured bus result.

Physical hardware, calibration, measured prediction accuracy, a solar experiment and a fabricated PCB remain pending. Do not present simulator screenshots or software test results as a completed physical prototype.

## Three-minute software demonstration

1. Open the local dashboard and point out the development-simulator label.
2. Select Normal load. Explain voltage/current, estimated charge and reserve.
3. Select Limited backup. Wait about four seconds for the optional fan to switch off.
4. Explain that preserving the lamp means reducing optional consumption; no extra energy is created.
5. Request Restore fan. Show that the controller refuses when the full-load runtime would be too short.
6. Select Solar charging. Explain negative battery current and the no-future-charge runtime heuristic. It uses nominal remaining energy and omits some upstream losses, so it is not a guaranteed minimum runtime.
7. Select Sensor disconnected. Show unknown charge/runtime and optional output off.
8. Export CSV and identify its simulated source field.

## Upgrade to a physical review demonstration

- Replace the simulator with actual sensor readings on a current-limited bench supply.
- Record reference-instrument readings alongside sensor readings.
- Add the protected battery only after assembly checks.
- Demonstrate a real optional load switching under the local controller.
- Use the test plan to distinguish demonstrated measurements from unvalidated estimates.

If hardware is unavailable by review day, describe the demo as a software prototype and integration preparation. Do not claim battery or solar validation.

## Suggested slide content

| Slide | Content |
| --- | --- |
| 1 | Problem, revised title, intended small DC use case |
| 2 | Functional architecture and bought-versus-designed components |
| 3 | Current implementation, with simulated and physical work separated |
| 4 | Estimation and control method |
| 5 | Demonstration plus actual evidence available that day |
| 6 | Test plan, limitations, BOM and next-semester schedule |

The original SIH presentation has not been overwritten.
