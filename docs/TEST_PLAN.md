# Physical validation plan

Status: not executed. Leave every result pending until measured on actual equipment.

## Before connecting a battery

- Record exact part numbers, shunt markings, sensor addresses and polarity.
- Check continuity and unpowered resistance for unintended shorts.
- Verify converter rails on a current-limited supply.
- Check optional-load OFF behavior at power-up/reset.
- Check current-sensor range and driver/load startup behavior.
- Record the reference instrument model, range, accuracy and calibration status.

The newer simulations in `HARDWARE_PERFORMANCE.md` identify startup as a priority test. With the actual lamp, fan and ESP32 connected, use a lab oscilloscope to record the common 5 V rail, fan terminal voltage and ESP32 3.3 V rail at fan turn-on, plus current/duration with suitable equipment. A DMM or 1 Hz dashboard may miss the dip. The provisional common-rail screen is 4.75 V; also apply the actual fan/dev-board specifications and verify no reset. Check repeated-start fuse suitability separately. Record output capacitance, wiring lengths and converter model; do not treat simulated capacitance or current limits as measured specifications.

## Calibration record

Take measurements at several voltages in the pack's normal operating range and several safe load currents. Repeat positive and negative battery-current measurements using a suitable supervised setup.

| Run | Reference V | Reported V | Reference A | Reported A | Temperature | Error / correction |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | | | | | | |

Suggested voltage target: within 1%. Suggested current target: ±(3% of reading + 10 mA) over the intended range. These are targets, not achieved specifications.

## Charge and runtime

1. Establish full charge using the pack manufacturer's method and compatible charger.
2. Establish the capacity basis independently: `CAPACITY_AH` means capacity from verified full charge to the pack manufacturer's specified **normal discharge endpoint**, before the project's reserve is subtracted. This is a supervised capacity-characterization procedure with a separate suitable load/cutoff; do not bypass the project's operating limits or use BMS emergency cutoff as the endpoint. Until this is established, retain the pack's documented capacity as a provisional assumption and report that limitation.
3. Enter that capacity and reviewed current-calibration constants. **Do not enter only the Ah delivered from full charge to the project's 20% reserve as CAPACITY_AH**: the algorithm would subtract another reserve. Record partial-discharge Ah separately. Only infer total capacity from a partial interval when its charge endpoints are independently known.
4. Synchronize charge only after a real reference has been established.
5. Run steady-load trials, recording predicted runtime at defined checkpoints.
6. Compare predictions with actual remaining time to the same endpoint.
7. Repeat with changing loads; report separately from steady-load results.

| Trial | Initial reference | Load schedule | Predicted remaining min | Actual remaining min | Absolute error | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | | | | | | |

Do not validate charge against a second calculation from the same unverified sensor. Use independent charge-throughput/capacity measurements. Percentage runtime error near zero remaining time is unstable, so report absolute minutes as well.

## Control comparison

For the implemented two-policy comparison, use the production firmware's `MIN_H 0` for the baseline and `MIN_H 3` for priority control, restoring the optional branch after a valid full-charge reference. Both retain voltage/temperature/fault limits. `MIN_H 0` removes early runtime-based shedding; it does not bypass reserve protection. Stop both trials at the same independently tracked 20% reserve endpoint, or earlier if a normal voltage/temperature limit is reached. Hold starting charge, requested loads, controller supply arrangement and measurement method constant. First disconnect solar to remove weather variation, then conduct separate solar experiments.

A third fixed-reserve policy was an earlier proposal, not an implemented distinct experimental arm. At the same 20% test endpoint it duplicates the baseline; do not claim a three-policy result without defining and implementing a genuinely different test. Never force the optional GPIO high to obtain a baseline.

| Trial | Policy | Essential service min | Optional service min | Delivered Wh | Switching events | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | | | | | | |

Repeat trials and report variability. Stop at the chosen normal reserve; do not use repeated emergency BMS trips as the endpoint.

## Fault and reliability checks

| Test | Expected behavior | Physical result |
| --- | --- | --- |
| Required sensor unavailable | Optional output off; estimate invalidated | Pending |
| ESP32 reset | Output off; charge unknown | Pending |
| Laptop disconnected | With independently powered ESP32 and verified USB VBUS isolation, local policy continues. With USB-only power, reset/power loss leaves the fan off. | Pending |
| No serial telemetry >3 s | Dashboard displays stale data | Pending |
| Restore with inadequate margin | Refused | Pending |
| Threshold noise | No repeated automatic on/off cycling | Pending |
| Temperature input beyond configured limit | Optional output off | Pending |
| Two-hour supervised run | No crash or unexplained control action | Pending |

Use signal injection or controlled fixtures for fault inputs. Do not short or overcharge the battery, deliberately overheat it or exceed device ratings to demonstrate a warning.

## Final evidence

Save hardware photographs, the reviewed schematic, raw CSV files, instrument readings, calibration constants, firmware version and analysis plots. Keep simulated and measured datasets in separate directories and label them clearly.
