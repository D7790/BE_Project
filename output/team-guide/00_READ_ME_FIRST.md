# WattSense — start here, team

**Shareable team guide · 2 October 2026 · Review 3: 3 October 2026**

Team: Dhanesh Chaudhari, Yash Ahire, Mrudula Pagar and Ujjwal Kshirsagar. Department: Electronics and Telecommunication Engineering.

## The project in one sentence

**WattSense measures a battery-powered DC system and turns off an optional fan when backup becomes limited, so an essential lamp can operate longer.**

We design the monitoring/control interface PCB and software. We use a purchased protected battery, matched charger, ESP32 development board and external 5 V converter. We are not designing a custom BMS.

## Read these files in this order

| File | What you will understand |
| --- | --- |
| [01 — Project explained](01_PROJECT_EXPLAINED.md) | Problem, working flow, components and control decisions |
| [02 — Hardware and PCB](02_HARDWARE_AND_PCB.md) | What to buy, how the board was designed, connections and lab gates |
| [03 — Software and demo](03_SOFTWARE_AND_DEMO.md) | Firmware, dashboard, running the simulated demo and software checks |
| [04 — Simulation and testing](04_SIMULATION_RESULTS_AND_TESTING.md) | What the numbers mean and how we must verify them physically |
| [05 — Slides and viva](05_REVIEW3_SLIDE_GUIDE_AND_VIVA.md) | All 14 slides, speaking prompts and likely questions |
| [06 — Team plan and budget](06_TEAM_TASKS_BUDGET_AND_NEXT_STEPS.md) | Roles, Review 3 preparation, buying order and final-semester work |

For a quick first pass, read this page, 01 and 05. Then read your role's detailed guide. Everyone should understand the whole power flow and the difference between simulated and measured results.

## What is actually complete?

| Available in the full project | Still pending |
| --- | --- |
| Editable four-layer Rev B KiCad design and fabrication exports | Supplier/part selection, purchase, fabrication and assembly |
| ESP32 firmware source and successful recorded builds | Uploading to a qualified board and real operation |
| Local dashboard, teaching simulator and CSV logging | Calibrated real sensor data |
| Software, circuit and battery/load model checks | Startup, temperature and matched runtime measurements |
| Editable 14-slide presentation and research-paper draft | Experimental claims and publication/submission approval |

The latest full recorded technical audit is **30 September 2026**. These guides explain that evidence; creating them did not rerun the suite. No physical measurements have been supplied. Production hardware/solar enable flags remain false.

## What can we claim in Review 3?

Say: “We have completed the initial design, software and simulation work. We will now assemble and calibrate the hardware, then compare measured essential-load service.”

The model's longer lamp runtime is obtained by sacrificing fan runtime. It is not extra battery capacity or a measured 44% improvement. There is no implemented AI, appliance recognition or custom BMS. The project can support final-year work through implementation, calibration, fault handling and a fair experimental evaluation; simulation alone does not complete that work.

## Sharing and source files

Send the complete **WattSense_Team_Guide.zip** and ask teammates to extract it. All seven Markdown files are readable in a text editor; sibling links work in a Markdown viewer. This bundle contains explanations only, with no external image dependencies.

The ZIP does **not** contain code, CAD, the presentation, supplier quotations or raw results. Share the complete project separately before anyone tries the commands. In these guides, paths written in backticks are relative to that project's root folder.

Start from these full-project sources when details change:

- `docs/NEXT_STEPS.md` and `docs/RECHECK_2026-09-30.md`
- `hardware/pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md`
- `firmware/include/config.h` and `firmware/include/controller.h`
- `simulations/results/hardware-summary.json`
- `output/pptx/WattSense_Review_3_14_Slides_Presentation.pptx`
- `paper/READ_ME_FIRST.md`

The original SIH pitch contains older ambitions and is not the current build specification. Check the latest files and record any agreed changes so the team presents one consistent project.
