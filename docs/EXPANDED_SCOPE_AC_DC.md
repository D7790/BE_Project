# WattSense household energy signatures and battery runtime estimation

**Superseded later on 3 October 2026:** The user clarified that WattSense is a battery-mounted, battery-powered monitor/adviser, with solar or compatible AC/DC charging and AC/DC load paths. Use [the battery-centred scope](BATTERY_CENTRED_SCOPE.md) as the current plan. This document's standalone AC-first application and milestone order are historical; the valid sensing/current/isolation boundaries remain relevant. Existing DC evidence and code/CAD are preserved.

Scope updated **3 October 2026** for Group 7, guided by **Mahesh Sapte**. WattSense now targets household AC appliance signatures and energy estimation, alongside battery-side DC monitoring and backup-runtime estimation. This roadmap supersedes the earlier lamp/fan-only completion plan. Review 3 is on 3 October 2026; final submission is next semester on the department's official date.

The USP is connecting a measured appliance profile with its energy use and, when a compatible battery/inverter system is available, its effect on backup. The existing firmware, dashboard and Rev B PCB are a DC foundation. No AC measurement interface, real signature dataset or trained classifier has been implemented yet. No physical prototype or hardware measurements have been confirmed.

Use [the editable 14-slide Review 3 presentation](../output/pptx/WattSense_Review_3_Expanded_AC_DC_Checked.pptx) for this expanded scope. The prior DC-only presentations are retained as historical versions.

## What the expanded project will deliver

| Stage | Deliverable and evidence |
| --- | --- |
| AC energy monitoring | A properly rated AC meter records RMS voltage/current, **real power in W** and energy in Wh. Record power factor only if the selected meter provides it. Validate readings against an independent reference. |
| Known appliance signatures | Label recordings from 4–6 selected household appliances, initially one appliance per run. Include operating states and repeated sessions. Match only profiles supported by the measured data. |
| Energy estimation | Integrate real power over time or use the meter's validated energy counter. Distinguish this measured total from consumption attributed to an inferred appliance. |
| Signature recognition | Compare a Random Forest candidate with a Decision Tree and simple feature-matching baseline in local Python. Evaluate uncertain and unseen loads as well as known classes. |
| Backup estimation | Combine independently established usable battery energy with measured demand, or a stated usage scenario. Validate on a compatible, appropriately rated battery/inverter system. |
| Later extension | Test selected load combinations after single-load validation. Aggregate appliance attribution is a separate evaluation milestone; solar, cloud/mobile features and automatic mains switching are optional. |

Ordinary mains-powered monitoring can report appliance signatures and energy without a battery. Backup runtime applies when the loads are supplied by a documented battery/inverter or UPS arrangement. The first completion milestone is calibrated AC data plus a reproducible known-load evaluation; the backup experiment follows compatible equipment selection.

## Measurement and power boundaries

```text
Household AC source -> rated enclosed AC meter -> selected appliance
                              |
                 documented isolated low-voltage data interface
                              |
                      ESP32 or local collector
                              |
                  labelled records -> features -> classifier
                              |
                  profile / UNKNOWN -> Wh estimate -> dashboard

Compatible battery + appropriately rated DC sensor -> usable energy
Compatible inverter/UPS + measured AC demand -> backup estimate
```

This is a functional diagram, not mains wiring instructions. Select a meter with documented measurement ratings, resolution, update rate, calibration method and **galvanic isolation at the accessible data interface**. If isolation is external, the complete assembly must document it. An exposed UART/I2C pin or a chip name does not establish isolation. Use an enclosed test arrangement assembled and checked under college laboratory supervision. No custom mains PCB or custom BMS is required for this plan.

The INA219 measures a low-voltage DC bus up to 26 V; the existing board cannot connect to household mains. Its Rev B project ceilings remain **2 A battery-side** and **1.5 A continuous at 5 V**, subject to physical qualification. It cannot carry household-inverter battery current. Use an appropriately rated external DC sensor and power path, or borrow a compatible UPS/inverter whose measurement interfaces are documented. Keep the existing board confined to its qualified DC experiments. [TI INA219 documentation](https://www.ti.com/product/INA219)

A consumer lead-acid UPS charger must not charge the proposed 4S LiFePO4 pack unless the manufacturers explicitly establish that combination's compatibility. A borrowed UPS should retain its approved battery and protections. Confirm voltage, chemistry, charging, fuse/cable ratings and shutdown behaviour before any backup experiment. Measuring battery-side total demand includes inverter losses; it does not directly identify individual AC appliances.

An AC metering IC such as ADE9153A illustrates measurement capabilities, **not a selected component or a complete safe interface**. Meter/module selection and delivered cost remain open. [Analog Devices ADE9153A documentation](https://www.analog.com/en/products/ade9153a.html)

## Data and model plan

Choose appliances after checking the meter's resolution and update rate. Use features it can actually provide: mean/variation of real power and RMS current, state changes, event size and operating duration; power factor only when available. Do not claim harmonics, AC waveform trajectories or fast transient fingerprints from slow meter records. The existing DC firmware's nominal 10 Hz acquisition and approximately 1 Hz telemetry do not establish an AC sampling rate or a raw signature logger.

Record appliance identity/state, complete session identifier, timestamps, meter settings, supply conditions and independent reference readings. Split **whole sessions** between training and evaluation; neighbouring windows from one session must not leak across the split. Fit preprocessing and tune thresholds using training/development data, then preserve an untouched test set. [GroupKFold documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)

Random Forest is an initial candidate, not a committed winner. Compare it with the Decision Tree and feature baseline using held-out confusion matrices, macro F1 and per-class errors. Test unseen appliance types and overlapping states explicitly. Classifier probability alone does not guarantee correct recognition: an UNKNOWN rule needs validated confidence/distance or outlier criteria, with false-acceptance and rejection rates reported. [RandomForestClassifier documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)

Keep three calculations separate:

- **Measured AC energy:** integrate real W over time into Wh. RMS voltage multiplied by RMS current gives apparent VA, not generally real W.
- **Inferred appliance energy:** attribute energy using recognised states/profiles. Validate against independently metered appliance energy; identity errors can also cause attribution errors.
- **Backup runtime:** divide estimated usable energy by demand under an explicit scenario. For AC-side demand, include measured/assumed inverter efficiency and idle draw without double-counting losses. Report initial charge, capacity basis, reserve and uncertainty. Actual battery-side demand already includes upstream conversion losses.

## Build sequence and budget

1. **Review 3:** present the expanded architecture, sourced literature and existing software/CAD evidence. Identify AC measurements and classifier results as pending.
2. **October:** inventory laboratory access, borrow/quote a rated meter and isolated interface, check an enclosed test arrangement, and add raw AC logging. Calibrate before collecting training data.
3. **November:** collect single-appliance sessions, develop features, compare the three candidate methods and validate UNKNOWN handling.
4. **December to January:** validate Wh estimates; select a compatible UPS/inverter and properly rated battery-side measurement path; perform supervised matched runtime prediction tests.
5. **Next semester:** repeat held-out sessions, optionally evaluate selected combinations, report failures and complete the final report/demo by the official submission date.

The team budget remains **below ₹10,000**. The historical ₹9,700 allocation covers only the DC foundation and excludes the added AC meter/interface and household backup equipment. It is **not a complete expanded-project budget**. Prioritise AC metering and data collection; borrow lab/shared hardware and a compatible UPS where possible. Reallocate purchases after complete delivered quotes and compatibility checks. No new prices, purchases or proof of affordability are recorded here.

## Evidence and document alignment

The [30 September audit](RECHECK_2026-09-30.md) records 45 Python tests, 67 host C++ assertions, both firmware builds and CAD/model checks. Those are DC foundation results; their lamp/fan simulations do not establish AC signature accuracy, household energy savings or backup performance. Code, CAD and hardware-arming flags are unchanged by this roadmap.

The existing research paper, workbook copy guide and teammate guide describe the earlier DC scope. Their technical records remain historical evidence; their project-wide narratives and proposed evaluations need a follow-up revision before reuse for the expanded project. Update them only after retaining that distinction. The new Review 3 presentation is the communication path for the expanded scope.

Relevant signature literature already checked for the presentation: [Athanasiadis et al. 2021](https://www.mdpi.com/1996-1073/14/3/767), [Mollel et al. 2023](https://www.mdpi.com/1424-8220/23/10/4845), [Jaime et al. 2026](https://www.mdpi.com/2411-5134/11/2/29), [Xiang et al. 2026](https://www.mdpi.com/1996-1073/19/8/1883), and [Li et al. 2026](https://www.mdpi.com/1996-1073/19/13/3131). Their methods and reported performance are external evidence, not WattSense results.
