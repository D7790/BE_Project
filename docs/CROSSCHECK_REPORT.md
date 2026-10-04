# Wattsense cross-check — 28 September 2026

**Result: the current files pass the completed software and CAD checks after the corrections below. The project is a bench-prototype candidate, not physically validated hardware.** No parts were purchased, hardware flashed, supplier contacted or fabrication order placed during this review.

Scope: revision B's native schematic, four-layer board, BOMs, manufacturing package, firmware, Python simulator/server, calibration tool, simulations, dashboard, launch scripts and active lab instructions. Revision A remains the historical two-layer alternative; it was not redesigned or requalified in this review. The original rough SIH PPT remains a proposal, not an updated results presentation.

## Problems found and corrected

| Finding | Correction and evidence |
| --- | --- |
| The C++ state-of-charge accumulator used single precision. At the actual 10 Hz cadence, small charge increments could round away or accumulate biased error. Earlier one-second tests missed this. | Changed the charge accumulator and update arithmetic to double precision. A new one-hour, 10 Hz regression failed before the correction and now passes at 5 mA, 100 mA and 500 mA in both locked and armed test copies. This fixes arithmetic resolution; sensor offset/capacity uncertainty remains. |
| A valid JSON frame with a list/dictionary in `state` raised TypeError and could stop the serial worker. Boolean protocol numbers, fractional uptime and some contradictory values were accepted. | Added strict type, numeric and consistency checks. Malformed/deeply nested input becomes a rejected frame. A fake-serial test confirms that a following valid frame is still recorded. This tests software handling, not a physical UART. |
| The graph could include numeric fields from a frame marked `sensor_ok=false`. | Both chart scaling and line segments now omit unhealthy frames. Invalid readings appear as gaps. |
| Calibration could accept two copies of one validation setting; choosing the input filename as output could overwrite the raw worksheet. | Require two distinct validation settings and reject input/output path identity. New tests cover both cases. Reports hash the exact bytes used for fitting. Independent acquisition and instrument quality still depend on the operator. |
| Earlier instructions said to enter measured usable capacity without distinguishing total capacity from Ah delivered only to the 20% project reserve. | Defined CAPACITY_AH before reserve subtraction. Partial Ah to the project reserve is recorded separately; entering it as total capacity would apply reserve twice. See TEST_PLAN.md. |
| Older wiring/BOM/blueprint text permitted roughly 10 W of loads, inconsistent with the later PCB operating envelope. | Aligned current instructions to initial lamp/fan <=0.6 A each and total continuous 5 V loading <=1.5 A, including a battery-powered ESP32. The 2 A battery-path ceiling is separate. All require actual thermal/startup qualification. |
| The test plan implied laptop removal always permits continued operation, and described three experimental policies although only two distinct arms are presently implemented. | Distinguished USB-only power from independently powered operation with verified VBUS isolation. Defined the actual comparison as MIN_H 0 baseline versus MIN_H 3 priority, retaining all fault/reserve limits. A separate fixed-reserve strategy remains an optional future extension. |
| The earlier CAD audit did not explicitly compare every footprint field or prove the stated power-route widths. | Expanded footprint/value/BOM/interface and terminal mechanics checks. Added an independent graph traversal proving 20 explicit front-copper power/return paths at their documented minimum widths. |

No footprint, routing, board outline, component value or pinout correction was needed in the current revision B during this cross-check. Fresh checks and manufacturing exports were produced; the archive now includes the power-path validation record.

## Completed checks

| Check | Observed result | Limit of the result |
| --- | --- | --- |
| Python suite | **37 tests passed** | Synthetic fixtures and local HTTP/fake serial tests |
| C++ policy | **43 assertions passed: 16 locked + 27 armed-copy** | Host execution of production controller header |
| C++ INA219 reader | **24 assertions passed** | Fake register source; no electrical I2C emulation |
| ESP32 production build | RAM **22,164 B**, flash **323,053 B** | Compiles; no board flashed |
| ESP32 diagnostic build | RAM **21,960 B**, flash **303,189 B** | Compiles; fan output stays low by design |
| Full simulation suite | PASS; nine reduced SPICE runs and accelerated plant/fault cases | One deliberately tested old Rev A I2C corner remains outside the intended envelope; the suite correctly reports it |
| KiCad ERC / DRC | **0 / 0 reported violations**, 0 unconnected, 0 parity issues | Configured checks; inherited ignored categories remain disclosed in the CAD report |
| CAD component audit | 50 locations, 114 electrical pad assignments; values, footprints and BOM agree | Does not authenticate purchased parts or prove physical fit of substitutes |
| Copper/planes | Four copper layers; both inner GND fills are single connected polygons; 104 vias | Does not establish measured noise, EMC or temperature improvement |
| Power tracks | 20 intended power/return paths found on F.Cu at specified widths | Geometric continuity only; not an ampacity or thermal certification |
| Manufacturing archive | 12 fabrication files plus specification and two validation records; ZIP integrity checked | Vendor DFM, actual stackup, finish and delivered quote still pending |
| Dashboard | Normal display, priority shedding, refused restore and sensor-fault unknown estimates observed in the in-app browser; no captured console errors/warnings | Simulated data only; earlier mobile-layout checks are historical |
| JavaScript / launch scripts | JavaScript syntax and PowerShell parsing pass | Every launch script was not separately executed against physical devices |
| Calibration CLI | Four-channel synthetic example passes with simulated label retained | No physical calibration values entered or applied |

Production `HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false` remain unchanged. Total native C++ assertion count is **67**. See `../simulations/results/suite-summary.json`, `firmware-host-summary.json`, the revision B `reports/` folder and `evidence/crosscheck-record.json` for reproducible records and source hashes.

The ideal runtime result remains 4.879 h baseline versus 7.247 h priority, with fan shedding at 1.880 h. These are model outputs showing service traded from fan to lamp. They are not measured runtime, greater battery capacity or proof of a guaranteed backup time. The ideal plant omits voltage sag, electrochemistry, detailed shunt/copper/fuse losses, ageing and hardware uncertainty. The reduced switch model is not an actual BLDC fan or vendor MOSFET model.

## Manufacturer cross-checks

- [TI INA219 datasheet](https://www.ti.com/lit/ds/symlink/ina219.pdf): SOIC pin mapping, addresses 0x40/0x41/0x44, voltage/current register scaling, 3.3 V operation and 26 V input ceiling agree with the design. The library's “32 V / 2 A” calibration name does not authorize 32 V at the pins. Configuration/calibration constants were also checked against the pinned local Adafruit source.
- [AOS AO3400A datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf): documented low-gate-voltage on-resistance supports the 3.3 V drive choice; actual startup and temperature remain untested.
- [Vishay WSL datasheet](https://www.vishay.com/docs/30100/wsl.pdf): selected 2512 family has the stated 1 W reference rating. At 2 A, each 0.1-ohm shunt dissipates 0.4 W; two series shunts lose 0.4 V and 0.8 W before other losses. Derating and solder temperature remain physical checks.
- [Littelfuse 466 datasheet](https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f): 1206 package, 1 A/2 A selections and continuous-current derating match the BOM assumptions. Startup pulses and fault coordination still need review with the actual converter and load.
- [Phoenix 1715721](https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-15-2-508-1715721) specifies 5.08 mm pitch and 1.3 mm PCB holes; both match all six terminals. [Panasonic EEUFR1E470](https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1E470) has the selected 5 mm body and 2 mm lead pitch.
- [Vishay SS14](https://www.vishay.com/docs/88746/ss12.pdf) and [SMBJ15A](https://www.vishay.com/docs/88392/smbj.pdf) package/polarity/rating references agree with the chosen footprints and intended use. A TVS is not reverse-polarity blocking or complete overvoltage protection; surge, fuse-clearing and protection performance were not simulated or tested.

## Still required before claiming a working project

1. Confirm exact purchased parts, common-port pack/charger compatibility, converter regulation/current limiting, actual fan startup and delivered prices. The INR 9,700 plan is an allocation ceiling, not a quotation; four-layer affordability and Pune 411048 delivery are unconfirmed. No live cart or vendor DFM review was performed.
2. Perform staged current-limited bring-up and independent meter calibration. Check real pull-up rise times, fault/reset behavior, wiring polarity and the USB supply arrangement. No reverse-polarity circuit is fitted.
3. Independently establish the capacity basis, charge reference and trial endpoint. Only the optional load is switched; the essential branch remains powered, so supervise and stop physical trials at the agreed normal endpoint.
4. Measure temperatures, actual estimation error and matched baseline-versus-priority service times. Do not claim the simulation's runtime gain as experimental evidence.

The design can proceed through the documented prototype process. It has not earned a claim of guaranteed operation, physical safety, production readiness or compliance. These are specific outstanding tests and purchasing decisions, not additional custom PCBs: the selected scope still needs one custom board plus a purchased BMS-equipped pack, matched charger and converter.
