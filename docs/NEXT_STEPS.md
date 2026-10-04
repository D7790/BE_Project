# Wattsense — finalized next steps

**Scope superseded on 3 October 2026:** Follow [the expanded household AC and battery DC roadmap](EXPANDED_SCOPE_AC_DC.md) for current milestones. The checklist below preserves the earlier lamp/fan DC foundation. Its ₹9,700 allocation excludes AC metering/interface and household backup equipment, so it is not the expanded-project budget. The Rev B 2 A battery path must not carry household-inverter current. Recheck equipment selection and delivered affordability before purchasing; existing DC assembly procedures remain relevant only within their qualified limits.

28 September 2026. This is the execution checklist for four students, Pune 411048, with a total budget **below Rs10,000**. Use `FINAL_AUDIT.md` for the audited status. No physical parts, assembly or experimental results have been confirmed.

## Freeze the core scope now

Build **one Rev B four-layer sensor/control PCB**, a classic ESP32, powered DS18B20, external regulated 5 V converter, purchased protected common-port 4S LiFePO4 pack and its supplier-matched charger. Use one essential lamp and one optional fan. Begin with approximately **2.5 W / 0.5 A class loads**, then verify their actual voltage/current requirements and startup demand.

No additional custom BMS, charger or converter PCB is required. Keep AI, universal appliance detection, cloud services, extra load channels and a mobile app outside the core completion criteria. Solar is a later compatible borrowed/purchased addition, not a demonstrated feature or a funded initial purchase.

Current limits remain: 2 A battery-side path ceiling; 1.5 A total continuous 5 V current including a battery-fed ESP32; initial measured lamp/fan current no more than 0.6 A each. These are project ceilings to qualify, not proof of thermal capability. The fan's switched return must not have another ground/data connection.

## What to do first

| Order | Action | Owner | Evidence / condition for moving on |
| --- | --- | --- | --- |
| 1 — today | Confirm Review 3 date and required deliverables with the guide; present the narrowed scope | D, with all four | Actual rubric/date written down; no assumption that parts will arrive before review |
| 2 — today | Inventory lab supply, multimeter, soldering/magnification, oscilloscope and capacity/load-test equipment | A + C | Instrument access and supervision arranged; borrow a scope for startup measurements |
| 3 — today | Run the saved demo; each member explains power flow, current sign, reserve and fan shedding | B + D | Reproducible simulator demo and a short recorded backup, clearly labelled simulated |
| 4 — in parallel | Obtain delivered PCB batch and exact component BOM quotes; check pack/charger and load specifications | A | Full payable total and compatibility checklist below, before ordering |
| 5 — while sourcing | Bring up ESP32, temperature probe and buttons; keep diagnostic fan command OFF | B | Raw serial records with actual part photos; an empty INA scan is expected before the sensor PCB exists |

The first battery-free engineering milestone is **an assembled Rev B board reporting sensor readings that agree with an independent meter on a limited bench supply**. Do not promise this before parts arrive. A borrowed INA219 breakout can support an earlier temporary measurement demonstration, but buying three extra modules is not required for the custom-board build.

## Purchase sequence and budget decision

Use `hardware/BUYING_PLAN_PUNE.md` and `hardware/SUPPLIER_QUESTIONS.md`. Existing prices are dated leads; delivery to 411048 is unconfirmed. No order or supplier message has been placed by the assistant.

1. Starter items: classic ESP32 exposing GPIO4/21/22/25/26/27, data USB cable, powered three-wire DS18B20, two normally-open buttons and suitable signal wire. The PCB already contains the pull-ups, sensor ICs and MOSFET driver.
2. Select a converter and small power-only lamp/fan using actual documentation. Verify input range, 5 V regulation, terminal-voltage range, startup current/duration and mounting. A printed current rating is not a qualified continuous/transient rating.
3. Quote **the whole minimum payable Rev B PCB batch plus one full populated-board BOM**, with spares, GST and delivery. Use its `BOM-grouped.csv` and exact SOIC-8 **INA219AIDR** ordering code. Check any substitute before purchase.
4. Buy the protected common-port pack and supplier-matched charger as a compatible pair after bench bring-up. The charger starts at no more than 1 A output. Do not buy the ambiguous charger lead merely because its output label says 14.6 V. The external near-pack fuse and manual disconnect are separate required parts.
5. Solar hardware comes after the battery experiment works and a compatible controller/panel is affordable or borrowed.

| Cost category, including its share of tax/delivery | Allocation ceiling | Confirmed payable amount |
| --- | ---: | --- |
| Entire four-layer bare-board batch | Rs2,500 | Pending quote |
| All parts for one populated PCB | Rs2,300 | Pending quote |
| ESP32, temperature probe and converter | Rs700 | Pending selection/delivery |
| Loads, wiring, buttons, external fuse/disconnect, mounting | Rs700 | Pending selection/delivery |
| Protected battery | Rs1,800 | Pending compatible pair |
| Supplier-matched charger | Rs1,000 | Pending compatible pair |
| Unallocated shipping/spares contingency | Rs700 | Reserved; do not double-count shipping |
| **Total planning ceiling** | **Rs9,700** | **Affordability not yet established** |

This allocation contains no funded PCB re-spin or solar purchase. If actual totals exceed the cap, borrow compatible equipment first and discuss a deliberate fallback with the guide. Do not silently order historical Rev A: it needs ordering-code updates and fresh verification. Keep requested Rev B as the current candidate.

Before a fabrication order, have the selected fabricator confirm 100 x 90 mm, four layers in the stated order, nominal 1.6 mm FR-4, copper minima, drill interpretation, finish, DFM and total delivered cost. Resolve any proposed change before production. The archive is a prototype quote package, not an automatic order authorization.

## Build and test in this order

Use the exact connector map in `hardware/pcb/wattsense-main-revB-4layer/ASSEMBLY_AND_BRINGUP.md`. The following are milestones, not replacements for that procedure.

| Stage | Work | Pass evidence |
| --- | --- | --- |
| A — unpowered inspection | Check parts, polarity, solder joints, shorts, connector pin 1 and fan return; leave JP1 open | Photos, continuity/resistance record, signed wiring checklist |
| B — logic only | USB ESP32 or isolated regulated logic test as documented; diagnostic firmware, no battery | 3.3 V correct, addresses 0x40/0x41/0x44, plausible temperature and both button states |
| C — 5 V side | J4 at 5.0 V, initially **100 mA limit and no loads**; add a small known load deliberately | Correct rail/fuse polarity, no heating/shorts, fan OFF at reset and with GPIO disconnected |
| D — battery-side bench | Battery and charger disconnected; J1 at 12–13 V, initially 100 mA with unloaded converter | Correct sign and independently checked U1/U2 readings as known loads are added |
| E — calibration | Collect independent fit and new held-out readings using the blank worksheet; apply reviewed candidate constants and remeasure | Voltage target ±1%; current target ±(3% of reference + 10 mA) over the qualified range; document instrument uncertainty |
| F — pack and reference | Lab review of common-port pack, charger, fuse/disconnect and grounding; verify supplier's full-charge procedure and capacity basis | Signed compatibility/wiring record; legitimate current-boot charge reference, not a guessed SOC |
| G — switching/startup | Enable production hardware control only after preceding checks, rebuild and re-establish the reference; start with a small load before the fan | Local OFF/restore, reset/fault OFF; scope captures at common 5 V, fan terminals and ESP32 3.3 V; no reset, actual device limits met |
| H — thermal/stability | At least 30 minutes at intended maximum load, then a supervised two-hour operation trial | Ambient and component temperatures within selected components' derated limits; stable logging/control; no unexplained events |
| I — comparison | Repeated matched `MIN_H 0` baseline and `MIN_H 3` priority trials, with solar disconnected initially | Independent common endpoint, lamp and fan service times, energy, error and temperature records |
| J — solar extension | Add the qualified solar controller's battery port at J2; follow its documented connection order | Correct signed charging measurements and separate changing-input experiments |

The 4.75 V common-rail value used in simulation is a provisional screen, not an ESP32 reset specification. Check actual fan/dev-board requirements and the 3.3 V rail too. A 1 Hz dashboard cannot qualify a millisecond startup event. Pulse suitability of the fuses must be reviewed for the chosen fan, not inferred from the simulation's resistor-only fuse model.

`HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false` remain in the delivered source. No fabricated measurements or example calibration constants should be copied into hardware configuration. Set the solar flag only for actual solar-controller operation; a mains charger is not solar energy.

The essential lamp is not automatically disconnected. Supervise and stop every discharge trial at the independently tracked normal reserve/operating endpoint. Do not use BMS emergency cutoff as the experiment's ordinary endpoint. Capacity entered in `CAPACITY_AH` is before subtracting the reserve, not only the Ah delivered to 20%.

## Review 3 deliverables

- Revised title and scope: battery monitoring and priority load control; explain what the purchased BMS does separately.
- Functional block diagram, current native schematic/PCB, BOM and fabrication/assembly plan.
- A short labelled software demo: normal, limited backup, refused restore and sensor fault; CSV export with provenance.
- Labelled simulation plots: pull-up design, startup counterexamples and battery/runtime comparison. State every load/battery assumption; the 5.48 h / 7.88 h example is simulated.
- Final audit, pending-measurement checklist, confirmed quotes if received, and team responsibilities.
- Actual lab readings only if genuinely collected. If parts are unavailable, clearly present a design/software/simulation review, not completed hardware.

**The original SIH PPT is not ready as the current results deck.** Update slides 2–3 to remove unimplemented AI, universal appliance recognition, cloud and custom-BMS claims; replace the architecture with the current system; qualify benefits as targets; correct the mismatched paper citation noted in the blueprint. The original file has been preserved. `REVIEW_DEMO.md` gives the content sequence.

## Four-person ownership and final-semester finish line

| Person | Owns | Must hand over |
| --- | --- | --- |
| A | PCB/assembly, exact parts, quotes, pack/charger compatibility and power wiring | Checked BOM, paid-cost record, photos and power-stage test sheet |
| B | Firmware, raw sensor checks, configuration and control behavior | Reproducible builds, configuration history and reset/fault/switch evidence |
| C | Independent calibration, startup/thermal and discharge experiments | Raw instrument readings, held-out validation and repeated trial datasets |
| D | Dashboard/logging, document consistency, review/report and schedule | Source-labelled plots, updated deck, limitations and reproducible demo instructions |

Finish the project with an assembled unit, independent calibration, repeated physical comparisons, startup/thermal/fault records, secure mounting, actual final BOM/cost, editable CAD/code, and a report that separates measurements from simulations. Solar needs real evidence if retained in the final submitted title/scope; otherwise agree the narrower battery-system title with the guide. Add optional ML only after the core acceptance work is complete.

## Commands and starting files

From the project folder:

```powershell
# Software demo; if already running, open its existing page instead.
.\run_demo.ps1
# Reproduce tests and labelled simulations.
.\run_simulations.ps1
# Build only; these do not upload to hardware.
.\build_firmware.ps1 -Environment bringup
.\build_firmware.ps1 -Environment esp32dev
```

Dashboard: `http://127.0.0.1:8765`. Hardware serial startup, calibration and the real COM-port procedure are in `LAB_START_GUIDE.md`. Close other programs holding the same serial port before switching between diagnostic tools and the hardware dashboard.
