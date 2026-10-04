# WattSense: Review 3 speaking guide and viva

Prepared **2 October 2026** for **Review 3 on 3 October 2026**. This follows the actual 14-slide `WattSense_Review_3_14_Slides_Presentation.pptx`.

**Remember:** we have software, a PCB design and simulations. Physical assembly, calibration and measurements are pending. Do not describe a simulation as a working hardware prototype.

## Explain the 14 slides

### 1. Title

WattSense means battery monitoring plus priority load control. Our example has an essential lamp and an optional fan.

**Say:** “WattSense monitors a battery-powered system and switches off an optional load to preserve essential lighting for longer.”

### 2. Introduction and topic overview

A battery stores limited energy. Running both devices consumes it faster. Our controller estimates remaining charge and backup time, then sheds the fan. The purchased BMS protects the cells; our board manages the load decision. The intended system is a small DC demonstrator.

**Say:** “We preserve lighting by reducing fan operating time when backup becomes limited.”

### 3. Literature survey 1: earlier energy-management systems

Marahatta supports priority switching; Rajbhandari uses forecasts and optimisation; Bai studies rule-based control and load shedding; Lv controls battery storage in a larger microgrid; Guo and Kors demonstrate a monitored teaching platform. A microgrid connects local sources, storage and loads.

**Say:** “Existing work establishes the principle. We apply it to a smaller, inspectable demonstrator.”

### 4. Literature survey 2: choosing a manageable method

These studies cover power/SOC rules, predictive optimisation, converter control, learning and network optimisation. Their different scales and requirements matter. Our initial controller uses explicit thresholds that we can understand and test; it does not implement those advanced algorithms.

**Say:** “We chose a simple rule so its behaviour can be checked with our available resources.”

### 5. Literature survey 3: estimating battery charge

SOC means state of charge. Coulomb counting tracks current over time: 1 A for one hour corresponds to 1 Ah. Movassagh explains accumulated error; the other studies examine battery models, parameter estimation and filtering. Sensor error, an incorrect starting charge and uncertain capacity can all affect our estimate.

**Say:** “Charge estimation requires calibrated current measurements and a valid starting reference.”

### 6. Literature survey 4: test the actual battery

Zine tests current integration on lead-acid batteries; Fahmy reports numerical estimation results; Wang examines LiFePO4 temperature effects; Turkmanović studies computation-rate tradeoffs; Bampi develops a battery-characterisation rig. Different batteries and processors prevent direct transfer of their accuracy claims.

**Say:** “These papers guide our testing, but their reported accuracy is not our achieved accuracy.”

### 7. Research gap and project focus

Priority switching and SOC estimation already exist. Our contribution is integrating a local controller, custom interface PCB, reproducible tests and a planned measured comparison. Fan startup, sensor errors and voltage drop can limit the real system.

**Say:** “We will evaluate the practical tradeoff between essential and optional service.”

### 8. Problem statement and objectives

The goal is longer essential-lamp service. Objectives are measuring signed current and power, estimating charge/runtime, controlling fan shedding and restore, handling faults, and comparing calibrated trials. Signed current distinguishes charging from discharging.

**Say:** “We must demonstrate both trustworthy measurements and correct switching behaviour.”

### 9. Methodology and architecture

Follow the arrows: protected pack → current-sensing PCB → external 5 V converter → lamp and fan. The ESP32 reads sensors and controls the fan MOSFET. USB carries data to a local dashboard; the laptop does not make the hardware control decision. The 100 × 90 mm, four-layer board is designed but not fabricated.

**Say:** “The fan turns off after estimated runtime stays below three hours for three seconds. Restoration needs a request, prospective full-load runtime of at least 3.25 hours, and valid operating conditions.”

### 10. Data collection and validation

The recorded audit reports 45 Python tests, 67 C++ assertions, successful firmware builds and agreement across 12,000 host comparison steps. These are computer checks, not ESP32 hardware measurements. Eighteen scenario pairs explore assumed parameters. Three of six startup models fail the provisional 4.75 V rail screen, identifying cases to investigate physically.

**Say:** “The models reveal limitations and guide the measurements we need next.”

### 11. Expected outcomes and evaluation

The model gives baseline lamp/fan service of 5.48 hours. Priority control gives 7.88 hours of lamp service and 2.49 hours of fan service: approximately **44% more lamp service and 54% less fan service**. Assumptions include 6 Ah, 68%–20% SOC, 90% efficiency, no charging, two 2.5 W loads and 0.8 W controller consumption. Calibration figures are targets, not achieved accuracy.

**Say:** “We trade optional service for essential service; we have not increased battery capacity or proved an efficiency gain.”

### 12. Project timeline

Review 3 presents design and software evidence. October is for confirming parts and bench assembly; November–December for calibration, startup and thermal tests; next semester for repeated trials and the enclosure. Final submission needs a measured working prototype.

**Say:** “Our next milestone is controlled physical assembly, followed by calibration and testing.”

### 13. References

The numbered references support the four literature slides. A DOI identifies a publication. Full citations are in the speaker notes. Understand the grouped lessons; do not read twenty references aloud or claim to have reproduced each study.

**Say:** “These sources informed our load-control approach, estimation limits and validation plan.”

### 14. Thank you

**Say:** “WattSense aims to preserve essential lighting through battery monitoring and optional-load control. Our next stage is hardware assembly and measured validation. Thank you.”

## Likely viva questions

1. **Is this a custom BMS?** No. We buy a protected pack; our PCB measures and controls the fan.
2. **Is hardware ready?** No. Design and software evidence exist; assembly and measurements remain pending.
3. **Are you using AI?** No. The controller uses defined rules.
4. **What is new?** Our integrated implementation and evaluation; priority switching itself already exists.
5. **Why ESP32?** It provides the sensor interfaces and control/output functions used by this design.
6. **What is an INA219?** A current/power monitor that measures voltage across a shunt resistor.
7. **Why not use voltage alone for percentage?** LiFePO4 has a relatively flat voltage region; voltage alone is insufficient for our estimate.
8. **What happens after restart?** Charge is unknown until a valid reference is established.
9. **Why three seconds?** The sustained condition avoids reacting to a brief threshold crossing; it still requires hardware evaluation.
10. **Why a restore margin?** Adding the fan increases demand; the controller checks runtime with that added demand before restoring it.
11. **Does the lamp stop automatically at reserve?** No. Trials need a supervised external stop.
12. **Why four layers?** Internal ground planes support routing and ground continuity; actual noise and temperature performance remain unmeasured.
13. **Is 7.88 hours guaranteed?** No. It is a simulation result under stated assumptions.
14. **What does it cost?** About ₹9,700 is a planning allocation, not a confirmed delivered purchase total.
15. **Why report failed startup cases?** They identify operating conditions needing better component selection or qualification.

## Three-minute software demo

- **0:00–0:30:** Open the local dashboard. Point out its simulated-data label and select **Normal load**.
- **0:30–1:15:** Select **Limited backup**. Wait roughly four seconds; explain why the optional fan switches off.
- **1:15–1:45:** Request **Restore fan**. Explain refusal when the prospective full-load runtime is insufficient.
- **1:45–2:20:** Select **Sensor disconnected**. Show unknown charge/runtime and optional output OFF.
- **2:20–3:00:** Export CSV and identify its simulated source field. Finish by stating which physical measurements remain pending.

Rehearse beforehand. This demonstrates software behaviour, not battery, fan or solar hardware performance.

## Source trail

Repository-relative paths: `output/pptx/WattSense_Review_3_14_Slides_Presentation.pptx`, `docs/REVIEW_DEMO.md`, `docs/PROJECT_FLOW.md`, `docs/RECHECK_2026-09-30.md`, `docs/HARDWARE_PERFORMANCE.md`, and `docs/TEST_PLAN.md`.
