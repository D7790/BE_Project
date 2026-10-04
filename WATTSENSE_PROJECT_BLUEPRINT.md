# Wattsense project blueprint

**Scope superseded on 3 October 2026:** Use [WattSense household energy signatures and battery runtime estimation](docs/EXPANDED_SCOPE_AC_DC.md) as the current project plan. This document preserves the earlier small DC lamp/fan foundation and its dated assumptions. Its scope restrictions, ₹9,700 allocation and comparison experiments do not define or validate the expanded household AC project. The research paper, workbook and team guides need follow-up narrative alignment. Existing code/CAD and recorded results are retained.

Prepared from the original SIH proposal; aligned to the implemented revision B on 28 September 2026. Use `docs/FINAL_AUDIT.md` for the final audit and `docs/NEXT_STEPS.md` for the current execution checklist. The original PPT is unchanged and still needs its claims updated before Review 3.

Initial team constraints: four electronics engineering students, no hardware or software built at the start, total hardware budget below ₹10,000, access to a college electronics lab, Review 3 in five days, final submission next semester. The SIH deck is a rough proposal and can change.

This is the implementation and validation plan. A runnable software foundation, simulator, serial dashboard and reference firmware now exist; see README.md. No physical battery prototype has been built or validated. Prices are planning allowances, and performance figures below are targets rather than achieved physical results.

PCB update (28 September): `hardware/pcb/wattsense-main-revB-4layer/` contains the current four-layer revision B with two internal GND planes and simulation-driven I2C pull-up changes. Native KiCad files, prototype fabrication exports and assembly guide are included. The original two-layer revision A is retained in `hardware/pcb/wattsense-main/` as a budget alternative. Both replace the three sensor modules and separate fan-driver module. Delivered cost needs a fresh quote; assembly, calibration and physical testing remain pending. See `docs/SIMULATION_REPORT.md` for the completed software/CAD checks and synthetic results.

## 1. Recommended project

**Wattsense: Battery Monitoring and Priority Load Control for Small Solar Systems**

Build a small solar battery system that measures how much power is available, estimates remaining backup time, and switches off an optional load when necessary to preserve an essential load.

An example demonstration:

1. A small battery powers an essential LED lamp and an optional fan.
2. The dashboard shows voltage, current, power, battery charge estimate and estimated backup time.
3. Turning on the fan increases measured power and reduces predicted backup time.
4. The user sets a minimum backup-time requirement.
5. If the predicted backup time falls below that requirement, the controller switches off the optional fan and records why it acted.
6. The lamp stays on. Subsequent controlled experiments measure how much longer it can operate.
7. Solar charging is added and measured once the battery-only system works.

This is a suitable final-year electronics project if you deliver calibrated measurements, a documented estimator, a working control circuit and repeatable experiments. A dashboard that only displays sensor readings would be a relatively basic project. The stronger academic contribution is the design and evaluation of the complete system.

Commercial battery monitors already calculate charge and time remaining. Therefore, do not claim that these functions alone are new. Your contribution can be an affordable implementation, local operation, a measured comparison of load-control policies, and a reproducible dataset. [Example of an existing battery monitor](https://www.victronenergy.com/media/pg/SmartShunt/en/introduction.html).

## 2. What changes from the SIH proposal

| Original proposal | Recommended treatment |
| --- | --- |
| “AI based battery management system” | Use the title above. Describe battery protection and energy management separately. |
| Voltage/current sensing and ESP32 | Keep. These are the foundation. |
| Battery percentage and runtime | Keep, but label them as estimates and validate them. |
| Solar energy monitoring | Keep for the completed project. Add after the battery demonstration works. |
| Automatic identification of any new appliance with zero setup | Remove from the core commitment. Consider classification of a few trained DC loads as an extension. |
| AI/LLM-generated recommendations | Start with transparent rules and calculated runtime consequences. An LLM is unnecessary. |
| Appliance-level sensors plus “nonintrusive” detection | Clarify the measurement method. Branch sensors directly meter loads; aggregate-only inference is a separate experiment. |
| Platform-agnostic and broad claims about households, farms and telecom systems | Demonstrate one specified small DC installation first. General compatibility remains future work. |
| Reduced bills and longer battery life | Treat as hypotheses. Measure essential-load operating time and curtailed energy first. |

Aggregate electrical measurements do not uniquely identify every appliance. Multiple devices can draw similar power, and simultaneous switching creates ambiguity. The research reference in your deck distinguishes measuring individual branches from inferring loads using one aggregate measurement. [NILM paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6720010/).

**Reference correction:** that linked paper is by Augustyn Wójcik, Robert Łukaszewski, Ryszard Kowalik and Wiesław Winiecki, published in 2019. The slide attributes it to Zeifman and Roth, so the citation needs correction. [Publication record](https://pubmed.ncbi.nlm.nih.gov/31434283/).

## 3. Do you need a custom BMS?

**No. Buy an assembled battery pack with an appropriate built-in BMS.**

These three parts have different jobs:

| Part | Purpose | Team action |
| --- | --- | --- |
| Battery BMS | Cell/pack protection and, where supported, balancing | Buy with the pack. Check its actual protection specifications. |
| Battery charger / solar charge controller | Applies the correct charging voltage, current limits and charging behavior | Buy a unit explicitly compatible with the selected pack. |
| Wattsense controller | Measures energy, estimates runtime, displays information and controls optional loads | Design and implement this yourselves. |

A basic BMS does not automatically provide an ESP32 with battery percentage, per-cell readings, a communications interface or a suitable charging profile. A listing saying “smart BMS” is insufficient evidence of Bluetooth, UART or CAN support.

Battery protection must work independently of your ESP32, laptop and network. Your load controller acts before normal operating limits are reached; it is not a substitute for battery protection. Manufacturer documentation treats the BMS, chargers and loads as interacting components with separate responsibilities. [BMS system guide](https://www.victronenergy.com/media/pg/Lithium_Battery_Smart/en/system-design-and-bms-selection-guide.html).

A custom BMS would add cell monitoring, balancing, protection circuitry, fault testing and PCB design. That could be its own final-year project, but it unnecessarily expands this project.

## 4. Hardware architecture

### Recommended electrical scope

- One assembled **4S LiFePO4 pack, nominal 12.8 V, approximately 6 Ah, with BMS**. “4S” means four cells in series.
- A pack-matched enclosed charger, typically a 14.6 V LiFePO4 charger for this class of pack. The pack manufacturer's instructions determine the exact settings and allowable current.
- A regulated **5 V load rail**, initially powering two standalone power-only loads: a small 5 V LED lamp and a 5 V fan. Keep the present scope to these two loads.
- Current PCB limits: start with approximately **2.5 W / 0.5 A class lamp and fan**, verifying actual steady current is no more than **0.6 A per branch**. A 3 W constant-power load can exceed 0.6 A after voltage drops. Total continuous 5 V loading, including battery-powered ESP32, is limited to **7.5 W / 1.5 A**. The battery-side path ceiling is **2 A**, subject to startup and thermal validation.
- One ESP32 development board.
- Three INA219AIDR ICs and three shunts already integrated into revision B: battery, converter input and charger input. All are physically fitted; solar telemetry stays disabled until a qualified solar controller is used.
- A battery surface temperature sensor and one AO3400A switching channel for the optional fan. The essential lamp is not switched by firmware.
- An optional/borrowed solar panel and compatible 4S LiFePO4 solar charge controller after the battery experiment works. A 20 W panel is an earlier sizing example, not a selected compatible part or an item funded in the initial budget.

The battery's nominal 12.8 V is not a regulated 12 V output. Use a suitable DC converter for the 5 V loads and ESP32 supply. This also avoids exposing ordinary 12 V devices to a pack's higher charging voltage.

### Functional power path

    Solar panel -> compatible solar charger -> S3 -> DC junction
                                                       |
    Protected battery pack <-> fuse + S1 <------------>+
                                                       |
                                                       +-> S2 -> 5 V converter
                                                                   |
                                                                   +-> ESP32
                                                                   +-> essential lamp
                                                                   +-> driver/switch -> optional fan

S1 measures signed net battery current, S2 measures total downstream consumption, and S3 measures the solar controller's net contribution at its battery connection. Place every battery charging and discharge path through S1. The enclosed mains charger is an alternative charging source connected on the system side of S1 according to the selected hardware's instructions; do not improvise simultaneous charger operation.

This diagram is a functional architecture, not a pin-level wiring schematic. Final terminal connections, return paths, fuses, switch ratings and grounding depend on the exact modules purchased.

S3 measures energy delivered by the controller, not raw panel power. Do not label it as measured panel-side power or use it to claim MPPT/conversion efficiency.

### Sensor choice

The current custom board uses **three INA219AIDR SOIC-8 ICs and 0.1-ohm shunts**. Documented INA219 breakout modules are an alternative only if intentionally building a temporary module prototype; do not buy them in addition to the native PCB sensors. Check the actual shunt resistance, resistor power rating, PCB/connector ratings and library configuration. Adafruit's reference board uses a 0.1-ohm shunt and supports a ±3.2 A measurement range; that does not establish the continuous thermal rating of every inexpensive clone. [INA219 reference design](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/overview).

INA226 is an acceptable alternative when a suitable board is available. Its shunt input range is approximately ±81.92 mV: a 0.1-ohm shunt therefore gives only about ±0.819 A full scale. A marketplace “20 A” headline must not override the actual board design. [TI INA226 datasheet](https://www.ti.com/lit/ds/symlink/ina226.pdf).

Keep the initial sensors on the battery-voltage side, below the raw solar input. Set distinct I2C addresses for multiple sensors and use ESP32-compatible 3.3 V logic levels. Verify positive and negative current with actual charging/discharging tests.

### Assembly requirements

- Buy an assembled pack; do not start by assembling loose cells.
- Fit a suitable DC-rated fuse close to the battery terminal and a manual disconnect. Choose ratings from the actual wiring and load requirements.
- Keep battery/load current off solderless breadboard rails and loose signal jumpers. Use secure power connections.
- Use a driver/module that actually accepts 3.3 V control. A relay coil must not be powered directly from an ESP32 GPIO.
- Provide the suppression/protection required by the chosen fan, relay and switching topology.
- Keep all external connections on the protected side of the BMS. Do not open the pack or connect to raw cell negative to simplify grounding.
- Have the lab supervisor check power paths and the grounding of the laptop, supply and instruments before connecting them together.
- Use a rated converter for the ESP32. Do not apply pack voltage to its 3.3 V/5 V pins.
- Demonstrate abnormal sensor inputs by software injection or a safe test fixture. Do not create battery shorts, deliberate overcharge or actual overheating.
- Stay with DC loads for this project. A mains inverter is unnecessary.

## 5. Software and estimation

### Review version

Use Arduino/C++ on the ESP32 and a simple laptop dashboard. A practical first path is:

    ESP32 -> USB serial -> Python collector -> CSV log + local dashboard

The implemented collector uses Python, pyserial and a local HTTP/browser dashboard; Streamlit is not required. Decisions run on the ESP32. Operation after laptop removal requires independent ESP32 power and a verified USB VBUS arrangement; USB-only power loss leaves the fan off.

After this works, add local Wi-Fi access or MQTT. Firebase and a phone app are optional. Paid cloud services and LLM APIs are not required.

Record at least: timestamp, battery voltage, signed battery current, total load power, solar-controller output power when fitted, temperature, estimated SoC, estimate validity, predicted runtime, load-switch state and reason for each control event.

Start with approximately 10 samples/second for measurement and integration, and refresh the dashboard about once/second. These are implementation starting points, not a claim that this sampling rate captures detailed motor or mains transients.

### Battery percentage

State of charge (SoC) is the fraction of the battery's charge remaining.

Coulomb counting tracks charge entering and leaving the battery:

    Ah change = signed current in A × elapsed seconds / 3600

For a discharge-positive sign convention:

    SoC_next = SoC_previous - 100 × I_discharge × dt / (3600 × measured_capacity_Ah)

Treat charging separately with an appropriate charge-efficiency assumption. Bound valid estimates to 0–100%, but flag missing measurements or uncertain initial state instead of hiding errors through clipping.

You need a known starting point, an independently established capacity basis, current-offset calibration and a defined synchronization method. `CAPACITY_AH` represents full-to-manufacturer-normal-discharge-endpoint capacity before the project reserve is subtracted; see `docs/TEST_PLAN.md`. Do not enter only the partial Ah delivered to the 20% reserve as total capacity. Do not set SoC to 100% every time the ESP32 restarts. If state is lost or the battery was used while monitoring was off, show “estimate unavailable / needs synchronization”.

Current-measurement errors accumulate. Voltage alone also does not provide a reliable percentage across the flat region of a LiFePO4 discharge curve. Commercial monitors likewise track current over time and require synchronization. [Battery-monitor operation and synchronization](https://www.victronenergy.com/media/pg/SmartShunt/en/operation.html).

### Runtime

A useful initial model is:

    Remaining runtime ≈ usable remaining battery energy / average battery discharge power

Use a calibrated energy estimate down to a defined operating reserve, not the entire nameplate energy. If using battery-side power, it already includes downstream converter losses and controller consumption; do not deduct those losses again.

For illustration only, 40 Wh available above the reserve and 10 W battery discharge imply about four hours at that load. Reducing measured discharge to 5 W implies about eight hours under the same assumptions. These are model examples, not measured prototype results.

When solar is active, separate “runtime if current solar conditions persist” from the “runtime without future charge” heuristic. The latter uses nominal remaining energy and measured load-branch power, omits some upstream losses, and is not a guaranteed minimum runtime. Near zero net discharge, show charging/sustained rather than an enormous or negative time estimate.

Use actual elapsed time and invalidate charge after missing data. The implemented firmware saves a diagnostic checkpoint but deliberately starts charge unknown after reboot; it does not trust saved charge while unobserved use is possible. The dashboard shows stale-data status.

### Load control

Implement a small state machine:

| State | Behavior |
| --- | --- |
| Normal | Essential and optional loads are available. |
| Reserve | Optional load is off because the backup-time requirement or reserve condition was reached. |
| Sensor fault | Optional load is off; mark predictions unavailable. Hardware protection remains active. |
| Recovery | Restore optional service only after a sustained recovery condition or explicit user action. |

The implemented controller requires the low-runtime condition to persist for 3 seconds, then latches the optional load off. Restoration is an explicit button/serial request and checks predicted runtime with the fan back on, including a 0.25-hour margin. There is no automatic restoration or override of hardware lockout, invalid readings or operating limits. Measure the actual optional-load power increment before enabling physical control.

The review can demonstrate load control by changing the configured minimum-runtime requirement. Label this as a policy demonstration. There is no need to deeply discharge a battery in front of the panel.

## 6. AI and research scope

The core project does not require AI. An explainable controller plus validated measurements and an experimental comparison can be a credible electronics project, subject to your department's rubric.

If your guide requires machine learning, select **one** extension after the core works:

1. **Forecast-assisted control:** predict near-term load from your collected history and compare against persistence/moving-average baselines. Only retain ML if held-out tests show a useful benefit.
2. **Known-load classification:** identify a few trained DC loads from aggregate measurements, with an “unknown/ambiguous” output.

Do not make both extensions mandatory. Do not use an LLM to decide battery safety limits or claim that coulomb counting itself is AI.

For load classification, start with one device changing state at a time. Then test combinations and simultaneous changes separately. Collect data across separate runs and operating conditions. Split training and testing by complete sessions, not neighboring samples from the same recording.

Branch sensors or switch logs can provide training labels, but the tested aggregate-only model must not receive those labels as input. Report performance separately for known loads, combinations and unseen loads. Household AC datasets are useful background, but they do not establish performance on your DC hardware. [UK-DALE dataset paper](https://arxiv.org/abs/1404.0284).

The implemented experiment compares the baseline and runtime policy below; see `docs/TEST_PLAN.md` for the exact firmware settings. A third fixed-reserve strategy remains an optional extension, not a completed implementation:

- A baseline that leaves all loads on until the chosen normal operating reserve is reached.
- Optionally, a separately implemented fixed-reserve controller with a clearly specified shedding threshold different from the common test endpoint. Using the same endpoint threshold duplicates the baseline and should not be counted as a third strategy.
- Your runtime-based policy, using the same loads, initial battery state and operating endpoint.

Measure essential-load operating time, optional service lost, delivered energy and the number of unnecessary switching events. Longer essential service is obtained by reducing optional consumption; it is not evidence of creating energy or improving battery capacity.

## 7. Budget and procurement

The authoritative current plan is `hardware/BUYING_PLAN_PUNE.md`: **Rs9,700 in allocation ceilings**, including the requested four-layer PCB and components, with solar purchases excluded/deferred. These are not delivered quotes. The earlier Rs9,500 module-and-solar plan is superseded and must not be added to or mixed with the PCB plan.

Get the entire payable PCB batch and component cost, not a single-board headline price. The pack/charger pair, external pack fuse/disconnect, terminals, cables, loads and shipping also count. A re-spin is not funded. If the sum exceeds the below-Rs10,000 budget, first borrow compatible equipment or discuss the documented fallback with the guide; do not silently change to an unreviewed PCB or charger.

Start with the classic ESP32, data cable, powered temperature probe and buttons. Use the college instruments. Quote the Rev B PCB and exact grouped BOM together; do not also purchase sensor breakout or fan-driver modules for this build. Buy the protected common-port 4S LiFePO4 pack and supplier-matched charger after bench bring-up. Current public leads and unsent supplier questions are in the hardware folder; no delivery to Pune 411048 is confirmed.

## 8. Review 3 preparation

Use `docs/NEXT_STEPS.md` and `docs/REVIEW_DEMO.md`. The original five-day period was a relative deadline provided on 27 September; the exact review date and departmental requirements must be confirmed by the team. Do not promise new PCB delivery for that review.

Demonstrate the existing local software, policy/fault behavior, current schematic/PCB, labelled simulation plots and the next lab procedure. If actual parts arrive, add only measurements genuinely completed on limited bench supplies. The old SIH PPT must be updated to remove unimplemented AI, universal appliance recognition, cloud and battery-protection claims; correct its research citation as explained above.

Assign one person to hardware/quotes, one to firmware, one to calibration/experiments and one to dashboard/evidence/presentation. Integrate daily. Everyone should explain both the battery power path and why longer lamp service costs fan service.

## 9. Next-semester completion plan

Fit these stages to the actual submission date; component delivery determines calendar dates.

| Stage | Work | Evidence required to move on |
| --- | --- | --- |
| Parts and manufacture | Exact part/pack compatibility, payable budget, vendor DFM and Rev B PCB order | Confirmed BOM, manufacturing specification and arrival plan |
| Bench bring-up | Inspect assembly, limited logic/5 V/battery-side supplies, diagnostic firmware | Checked rails, sensor addresses, temperature/buttons, default-off behavior |
| Calibration and switching | Independent meter data, candidate constants, small-load switching, scope checks | Held-out calibration results, startup traces, no reset, operating current limits met |
| Battery experiment | Qualified pack/charger, capacity basis/reference, matched baseline and priority trials | Repeated service times, energy, estimate errors and temperatures |
| Solar extension | Compatible borrowed/purchased controller and panel | Actual charging contribution and changing-input experiments; otherwise label pending |
| Final integration | Secure mounting/enclosure, repeat tests and presentation | Editable CAD/code/BOM, measured dataset, final report and reproducible demonstration |

No additional custom BMS, charger or converter PCB is required for this scope. Finish and evaluate the core system before adding ML, Wi-Fi or new load channels.

## 10. Definition of “the project works”

Agree on acceptance targets with your guide. Suggested targets follow; none have been achieved yet.

| Function | Suggested target | How to verify |
| --- | --- | --- |
| Voltage | Within 1% over the chosen pack operating range | Compare with a suitable calibrated/reference multimeter at several points |
| Current | Within ±(3% of reading + 10 mA) over the intended 0.1–2 A range | Check both directions using an independent current reference |
| Dashboard | Approximately one update per second, with stale-data indication | Time-stamped logs and a disconnect test |
| Charge tracking | Correct sign and elapsed time; explicit unknown state after reboot or lost measurement | Charge/discharge, reboot and missing-data tests |
| SoC estimate | Aim for ≤10 percentage-point error over a defined test cycle | Independently measured capacity and charge throughput; no self-comparison |
| Runtime | Aim for ≤20% error on held-out steady-load runs with enough time remaining | Compare recorded forecasts to actual time to the same reserve endpoint |
| Control | Optional load switches within 2 seconds after the configured sustained condition; no rapid chatter | Record repeated controlled events |
| Reliability | Two-hour demonstration run without crashes or unexplained switching | Logs and observation |
| Practical benefit | Quantified essential-service change and optional energy curtailed | Repeat comparable baseline/controller runs |

For runtime, report absolute error in minutes as well as percentage error; percentages become misleading near zero remaining time. Also test changing loads and solar variation and report their errors separately.

Do not validate an SoC algorithm only against values calculated by the same sensor and formula. Borrow a capacity tester/electronic load or use an independently measured discharge reference. If that reference is unavailable, report charge-tracking repeatability and runtime error, and state that absolute SoC accuracy is unverified.

Control comparisons require the same initial battery condition, reserve endpoint and requested load schedule. Stop each trial at that normal operating endpoint using the test procedure or a suitable load disconnect; do not use repeated BMS emergency trips as the test endpoint. Run several repeats. For early comparisons, keep solar disconnected to remove weather as a variable, then perform separate solar experiments.

Do not claim cell-level fault diagnosis, accurate state of health, remaining battery life, universal appliance recognition or quantified electricity savings unless you actually measure the required evidence.

## 11. Immediate next action

Follow `docs/NEXT_STEPS.md`: confirm the review rubric, inventory lab instruments, obtain the full payable Rev B quote/BOM, and start ESP32/temperature/button bring-up while the PCB is sourced. The next hardware milestone is **a current-limited Rev B board giving independently checked sensor readings**. Borrow a documented sensor breakout only if a temporary measurement demonstration is needed; it is not a prerequisite purchase for the PCB.

## 12. Custom PCB decision and remaining engineering work

Revision B is the requested four-layer **native sensor/control board**, not a plug-in module carrier. It integrates three INA219 ICs/shunts, fuses, one fan MOSFET, connectors and signal conditioning. ESP32 and converter connections use cables; their modules do not plug directly into an assumed footprint. The pack/BMS and charger stay external.

The design already exists. The next steps are mentor/exact-parts review, actual quote and vendor DFM, assembly, staged bring-up and measured validation. Use only Rev B's matching schematic, BOM and fabrication package. Historical two-layer A needs updating/rechecking if a budget decision selects it; it is not presently the final build.

Follow `hardware/pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md`. No board order or upload has been made. CAD consistency is not physical fit, thermal qualification or proof of startup behavior. Retain the 2 A battery-side ceiling, 1.5 A continuous 5 V ceiling and initial 0.6 A measured branch ceilings until the actual system is qualified.

### Other work your team must complete

| Work package | Required output |
| --- | --- |
| Requirements | A written voltage/current envelope, load priorities, operating reserve and demonstration scope |
| Component selection | Exact part numbers, compatible charging equipment and a costed BOM |
| Circuit engineering | Schematic, power/current calculations, driver choice, fusing and interface assignments |
| Firmware | Calibrated sensing, timestamps, state estimation, local control, reset behavior and fault handling |
| Dashboard | Live measurements, estimate validity, graphs, control-event reasons and exportable data |
| Experiments | Independent measurement checks, real runtime tests and a fair baseline/control comparison |
| Final assembly | Secure wiring or PCB, accessible disconnect, enclosure and useful labels |
| Academic documentation | Literature review, method, design decisions, measured results, limitations, source code and demonstration video |

For a PCB version, also deliver the editable schematic/layout, BOM, Gerber and drill files, assembly drawing and board-test record.

The team's own engineering contribution should be visible in the circuit decisions, firmware, estimator and evaluation. Using bought modules is compatible with that contribution; simply wiring modules together without explaining or testing their behavior is insufficient evidence of it.
