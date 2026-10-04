# Publication evidence recheck — 30 September 2026

**Verdict: the checked sources, native CAD and recorded numerical results support a reproducible design-and-simulation study. They do not support a hardware-validated prototype paper.** No physical measurements, purchases, calibration data or experimental trials were added in this recheck.

This review was independent of the main test-suite rerun. It did not import the project model implementation for its algebra/quadrature checks and did not modify native CAD, production firmware or prior audit records. The reproducible script is `verify_evidence.py`; machine evidence and input hashes are in `publication-evidence-check.json`. Fresh KiCad reports are `erc.json` and `drc.json`.

## Rechecked evidence

- All source, native-CAD, audit-evidence and document hashes in the 28 September checkpoint matched when this review ran.
- The 15-entry fabrication ZIP passed CRC checks and matched its recorded SHA-256. Its 12 manufacturing files match the saved exports byte for byte; native-source hashes and power-path audit provenance agree.
- Fresh KiCad 10.0.6 ERC and DRC report zero violations, zero unconnected items and zero schematic-parity differences. The calls include all severities and exclusions; DRC refills zones in memory without saving the board. The native files retain their checked hashes. Four configured ERC ignored categories and five DRC ignored categories remain disclosed in the JSON reports; no ignored category was added here.
- The hardware DC table and all 18 sensitivity rows agree with their raw CSVs. Runtime endpoints and the fan-shedding event agree with the saved traces. Independently solved 5 V circuit values agree with the summary; independent Simpson integration predicts both runtimes within one second. The OCV integral gives 37.4076 Wh over the chosen state-of-charge interval.
- All six startup trace extrema agree with the reported summary; current balance at the settled startup point agrees within 1 microampere. Three cases pass and three fail the provisional common-rail screen. A passing numerical test suite deliberately includes detecting these failing scenarios.
- Production flags remain `HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false`.

## Defensible headline result

For the illustrative 6 Ah, 68%-to-20% discharge scenario, with 90% converter efficiency, 0.10 ohm battery/BMS resistance, 2.5 W constant-power lamp, 2.5 W constant-power fan and 0.8 W controller demand:

| Quantity | Baseline | Priority control |
| --- | ---: | ---: |
| Essential lamp service | 5.47639 h | 7.88361 h |
| Optional fan service | 5.47639 h | 2.49361 h |
| Total delivered load energy | 31.76306 Wh | 32.24994 Wh |

Lamp service increases by **43.9564%**, while fan service decreases by **54.4661%**. Lamp energy increases by 6.01806 Wh and fan energy decreases by 7.45694 Wh. This is a redistribution of service under the stated assumptions. It is not an increase in battery capacity, an equal-service efficiency improvement, or an experimental gain.

The 18 deterministic sensitivity pairs span baseline service from 3.86667 to 5.79778 h and priority service from 6.28361 to 8.20306 h. These ranges are scenario outcomes, not confidence intervals or repeatability statistics. In every capacity scenario the estimator is deliberately given the true capacity; the sweep therefore does not evaluate estimator robustness to unknown capacity.

## Claim boundaries to preserve in the paper

1. **Battery model:** the piecewise OCV curve is explicitly invented for illustration; battery/BMS and wiring resistances are assumed. It is not a characterised LiFePO4 pack model. Do not call the runtime predictions a validated real-world accuracy result.
2. **Sensor model:** the main runtime comparison supplies exact current and capacity to the estimator. Agreement between estimated and simulated true SOC follows from this construction. Separate error examples demonstrate a limitation; they do not establish an accuracy specification.
3. **Converter and fan:** discharge/DC calculations use constant delivered power and fixed conversion efficiency. Startup uses a separate instantaneous current-limited behavioural source and voltage-dependent resistive fan demand. Neither is a measured converter control loop or BLDC model. Their outputs must be described as separate reduced scenarios, not one validated full-system simulation.
4. **Startup acceptance:** 4.75 V is a provisional *common-rail* screening floor. It is not an ESP32 reset voltage or fan acceptance threshold. In the smaller-load startup example the common rail reaches 4.79072 V while the fan terminal reaches 4.55124 V; a common-rail pass therefore does not qualify a selected fan. The smaller-load DC case gives 4.74610 V at the fan terminal. Actual permitted load voltage and startup/restart behaviour remain to be tested.
5. **Copper model:** it sums selected explicit front-copper paths. Planes/pours, pad spreading, contact variation, via paths, inductive parasitics and self-heating feedback are absent. Fixed 20 C and 60 C cases are parameter choices, not predicted temperatures. Additional PCB layers alone establish neither ampacity nor reduced noise.
6. **Protection:** only the optional fan is switched. At the reserve endpoint, the numerical experiment stops externally; the essential lamp is still connected in the design. The purchased protected pack and supervised stopping procedure remain necessary. This is not a custom BMS, cell-balancing system or safety certification.
7. **Implemented scope:** there is no measured solar harvesting, MPPT, AI forecasting or physical cloud/IoT experiment. The third sensing channel is provisioned but disabled in production configuration. Future work must be labelled accordingly.
8. **Statistics and originality:** numerical convergence and deterministic sensitivity are evidence of implementation consistency, not empirical validation or statistical significance. This review cannot establish scholarly novelty or plagiarism clearance; literature/citation review and an institutional similarity service are separate tasks.

## Appropriate publication positioning

A truthful title should use terms such as “design,” “simulation study,” or “reproducible evaluation.” Describe contributions as the integrated reproducible design, explicit priority-control experiment, service trade-off, and circuit constraints that guide later hardware selection. Avoid “experimentally validated,” “prototype demonstrated,” “improved battery efficiency,” “novel BMS,” or unsupported superiority to prior work.

Before a hardware-validation submission, obtain independent sensor calibration, measured operating/startup rails and temperatures, real component and battery characteristics, repeated matched baseline/priority trials with both loads' service reported, and reproducible raw experimental data. Authors must approve the final manuscript, attribution and target venue requirements.
