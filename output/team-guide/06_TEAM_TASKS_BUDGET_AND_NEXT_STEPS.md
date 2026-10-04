# WattSense — team tasks, budget and next steps

**Plan prepared 2 October 2026. Review 3 is 3 October 2026.** Final submission is next semester; agree its exact date with the department. The current plan starts from no purchased parts or physical measurements.

## 1. Assign one owner to each workstream

These are proposed roles, not existing assignments. Dhanesh, Yash, Mrudula and Ujjwal should choose one owner per row and one reviewer. Everyone should be able to explain the full system.

| Owner to choose | Responsibility | Concrete handover |
| --- | --- | --- |
| Hardware/PCB owner | Exact parts, quotations, assembly, wiring and current-limited bring-up | Confirmed BOM, assembly checklist, photos and measured rail values |
| Firmware owner | Sensor acquisition, configuration, reference procedure and fan policy | Build/version record, qualified firmware and fault/switching logs |
| Measurement owner | Independent calibration, capacity reference, startup/temperature and runtime trials | Raw readings, instrument details, scope traces and comparison tables |
| Dashboard/documentation owner | Local server, CSV integrity, presentation and report | Repeatable demo, correctly labelled datasets and updated figures/slides |

The measurement owner and hardware owner review wiring together. The firmware owner and dashboard owner check that recorded source labels and units are correct. A successful screen demonstration is not a substitute for the physical measurements.

## 2. What to finish before Review 3

- Read guides 00, 01 and 05 together. Agree the one-sentence project explanation and current status.
- Rehearse the **14-slide** presentation. Use `output/pptx/WattSense_Review_3_14_Slides_Presentation.pptx`, incorporating only the team's intended local edits.
- Run the **SIMULATED** dashboard once on the presentation laptop. Demonstrate limited backup, restore refusal and sensor fault. Keep the terminal running during the demo.
- Have the KiCad design and saved simulation chart available if asked. Explain that fabrication and real testing are pending.
- Carry the editable PPT, a presentation backup and these guides. Do not depend on PCB delivery or new hardware assembly before the review.

Each member should answer: what switches, why it switches, who makes the decision, how SOC is estimated, what has actually been tested, and what the next experiment is.

## 3. Budget: a ceiling, not a confirmed price

The team limit is below ₹10,000. These existing allocations reserve **₹9,700** in total. No fresh supplier prices or delivery estimates were checked for this guide.

| Category | Allocation ceiling |
| --- | ---: |
| Delivered four-layer bare-PCB batch | ₹2,500 |
| All components for one populated PCB | ₹2,300 |
| ESP32, temperature probe and qualified 5 V converter | ₹700 |
| Lamp/fan, wiring, buttons, external fuse/disconnect and mounting | ₹700 |
| Protected battery pack | ₹1,800 |
| Supplier-matched enclosed charger, initially no more than 1 A | ₹1,000 |
| Remaining shipping/spares contingency | ₹700 |
| **Total** | **₹9,700** |

Include tax, payable batch quantities and allocated delivery in each quote; count shared shipping once. College tools and team assembly labour are assumed. Solar purchases and a PCB re-spin are not funded. Below-₹10,000 completion remains unconfirmed until exact compatible parts and delivered totals are quoted.

Obtain the complete Rev B BOM before ordering. The PCB already includes three INA219 ICs and the fan switch, so buying three sensor breakout boards and a separate MOSFET module would duplicate the chosen design. Check footprints and exact part variants, not listing names alone.

Ask suppliers for delivery to **Pune 411048**. No delivery date is currently verified. If the total exceeds the budget, first investigate borrowing a compatible battery/charger or lab equipment. Any substitute or two-layer fallback requires an explicit design/BOM review; do not send historical Rev A files to fabrication without updating and checking them.

## 4. Build in this order after Review 3

| Gate | Work | Evidence required before moving on |
| --- | --- | --- |
| A — Select | Confirm exact pack/BMS/charger, converter, loads, BOM and fabricator | Compatibility, payable total, delivery and fabrication review |
| B — Assemble | Inspect unpowered PCB; test logic and low-current rails using the assembly guide | Correct polarity/continuity, sensor identities and rail readings |
| C — Measure | Calibrate sensors and validate on independent readings | Calibration report and held-out errors |
| D — Qualify power/control | Review fused battery wiring, establish charge reference; test controlled switching and faults | Verified startup/reset behaviour and oscilloscope captures |
| E — Qualify operation | Maximum intended load and supervised endurance | Temperature records, at least 30 minutes at intended maximum load and two-hour supervised operation, assessed against actual component limits |
| F — Evaluate | Repeated matched baseline/priority runs without charging | Independently tracked common endpoint, lamp/fan service and raw logs |
| G — Finalise | Compare measured/modelled results; document limits and changes | Final hardware demonstration, report, code/CAD archive and presentation |

These are completion gates, not promised calendar dates. Procurement and findings may change the schedule. The full `ASSEMBLY_AND_BRINGUP.md` and `docs/LAB_START_GUIDE.md` control the exact sequence and configuration changes. Keep `HARDWARE_CONFIRMED=false` until their prerequisites pass; changing the flag is not a substitute for qualification.

Do the core battery/lamp/fan system first. Solar is an optional later extension after the core evidence exists. A solar charge controller must match the pack and its charging requirements.

## 5. What “finished” should mean next semester

The completed project should have an assembled, documented PCB; calibrated measurements; repeatable load control and fault handling; startup/temperature qualification; and repeated fair runtime comparisons. The report should show both the lamp benefit and lost fan service, with assumptions and limitations.

There is already an IEEE-style **design/simulation research-paper draft**. Editable Word and PDF versions exist in the full project. It has no new physical results and has not been submitted. Author/guide review, venue requirements and institutional similarity review remain pending. The limited local originality check is not a global plagiarism certificate.

Update the paper and slides only with evidence actually collected. Keep original raw files, record revisions and have another teammate review each new claim.

Full-project references: `docs/NEXT_STEPS.md`, `hardware/BUYING_PLAN_PUNE.md`, `hardware/SUPPLIER_QUESTIONS.md`, `docs/LAB_START_GUIDE.md`, `docs/TEST_PLAN.md` and `paper/READ_ME_FIRST.md`.
