# Wattsense final audit — 28 September 2026

**Verdict: the current Rev B design, code and recorded simulations pass the completed checks. Proceed to exact-part selection, quotation and supervised prototype bring-up. Physical performance, charging compatibility and completion below Rs10,000 are still unverified.**

This is the current audit entry point. Follow [NEXT_STEPS.md](NEXT_STEPS.md) for the finalized purchase/build sequence, four-person ownership and Review 3 deliverables. Earlier audit reports are historical checkpoints; their smaller test counts do not supersede this one.

## What was audited

The native Rev B schematic and four-layer PCB, BOM/manifest, component/interface mapping, power paths, manufacturing ZIP, firmware and diagnostic build, serial collector, calibration safeguards, dashboard code, original/new simulation models, launch scripts and active project instructions. Hardware, software and simulation received separate independent reviews.

The original SIH PPT was checked against its previously extracted content and the revised scope. It remains unchanged and contains unimplemented claims; it is not an updated final-results deck. Historical Rev A was not requalified. No purchases, supplier messages, quote uploads, flashing or physical tests were performed.

## Corrections made in this audit

| Finding | Final correction |
| --- | --- |
| The blueprint still contained a superseded Rs9,500 module/solar budget, module-carrier assumptions, extra switches/sensors, a Streamlit suggestion and an old immediate-action sequence. | Aligned it to the actual native-sensor Rev B board, one fan channel, current Python/browser implementation and the Rs9,700 allocation ceiling excluding solar purchases. Removed conflicting procurement/schedule instructions. |
| Older blueprint guidance still allowed 3 W starter loads, despite the newer modeled voltage drops. | Start around 2.5 W / 0.5 A class lamp/fan; measure <=0.6 A per branch. The existing 1.5 A continuous 5 V and 2 A battery-path ceilings remain unchanged. |
| PCB requirements retained the old INA219AID ordering code and could imply that the near-pack fuse was on the PCB. | Corrected to INA219AIDR and distinguished onboard 5 V fuses from the mandatory external pack fuse/disconnect. No native circuit/BOM change was needed. |
| One assembly paragraph said to use 2 A for initial 5 V checks, conflicting with its detailed unloaded 100 mA stage. | All initial unloaded J4 guidance now starts at 100 mA; increase deliberately with known loads. |
| The configurable discharge simulation still labelled its endpoint literally as 20% and used a literal voltage threshold in its stop test. | Stop logic and endpoint labels now use the controller's configured reserve/voltage limits. The current default numerical results are unchanged. |
| Validation/checkpoint documents mixed historical and current counts/plans. | Added this audit, one execution checklist and clear links; historical records remain labelled. Blueprint charge persistence now agrees with the deliberate unknown-on-reboot behavior. |

No new material firmware, backend or native-CAD defect was found by the independent reviews. This is a bounded audit conclusion, not a claim that all possible defects have been eliminated.

## Verification evidence

| Check | Final result | What it does not establish |
| --- | --- | --- |
| Python regression suite | **45 tests passed** | Actual electrical behavior or calibration |
| Native C++ tests | **67 assertions passed**: 16 locked policy + 27 armed-copy policy + 24 register-reader | ESP32 instruction/peripheral timing or physical fan state |
| Additional telemetry boundary review | 322 field mutations produced no unexpected exception in the independent review | Exhaustive protocol/security correctness |
| Production ESP32 build | SUCCESS; RAM 22,164 B; flash 323,053 B | No hardware was flashed |
| Diagnostic ESP32 build | SUCCESS; RAM 21,960 B; flash 303,189 B | GPIO/rail behavior still needs measurement |
| Full simulation suite | PASS: nine earlier reduced circuits, six added startup cases, ideal/nonideal plants, faults and plots | Full battery, PWM converter, BLDC, thermal, EMC or protection emulation |
| Independent simulation checks | 15 checks pass; runtime quadrature agrees within 0.74 s; all six startup traces satisfy current balance | Accuracy of assumed battery, wiring and purchased-module parameters |
| Fresh KiCad ERC / DRC | **0 / 0**, unconnected **0**, schematic parity **0** | Manufacturing fit, ampacity or physical protection qualification |
| Native component/interface audit | **50 component locations, 114 electrical pin assignments, 19 nets**; values, footprints, BOM and firmware interfaces agree | Authenticity or fit of purchased/substitute parts |
| Copper and power paths | Four layers, 104 vias, both inner ground fills connected; **20 explicit front-copper power/return paths** checked | Measured heating or noise improvement |
| Fresh fabrication exports versus saved package | All **12 fabrication files match** after excluding generated timestamp metadata only | Vendor DFM and as-fabricated stackup/quality |
| Prototype ZIP | **15 entries**, CRC/content/source checks pass | A fabrication order or assembly approval |
| JavaScript and six PowerShell entry scripts | Syntax/parsing pass | Every script exercised against actual hardware |

Default ignored ERC/DRC categories are disclosed in the fresh JSON reports; no new exclusions were introduced to obtain these results. Native CAD and fabrication-package bytes are unchanged by this audit. The reviewed ZIP SHA-256 is `67104e14f3a16d4c21f371d1b55bd28e5f06980c7c53ddc32208ecef1b4bc20a`.

The passing simulation suite includes detecting deliberately bad scenarios. Three of six startup cases fail the provisional common-rail screen, and the older Rev A high-capacitance pull-up case misses its timing screen. These are useful counterexamples, not hardware passes. The smaller-load example remains **5.48 h baseline lamp service versus 7.88 h with priority control, fan shed at 2.49 h**, under its published assumptions; no experimental runtime gain is claimed.

Browser visual observations are retained from the earlier desktop/mobile reviews and are not newly performed here. Dashboard source and protocol behavior were reviewed, and the current automated HTTP/serial tests pass. No UI changes were made during this audit.

Current software/CAD/model source hashes, build logs and evidence links are consolidated in [final-audit-record.json](evidence/final-audit-record.json). Fresh CAD and independent model records are in [the audit evidence folder](evidence/final-audit/pcb-verification.json). The complete suite's current source manifest is [suite-summary.json](../simulations/results/suite-summary.json).

## Finalized design versus pending decisions

**Selected core:** Rev B four-layer board, three onboard INA219AIDR channels, one optional fan MOSFET, classic external ESP32, powered DS18B20, external 5 V converter, protected common-port 4S LiFePO4 pack and matched charger. No extra custom BMS/charger/converter PCB is required.

**Still to select or confirm:** exact converter, fan/lamp and their permitted voltages/startup demand; pack/charger compatibility and connectors; external fuse interrupt rating and wiring; physical component fit; final vendor stackup/finish/DFM; delivered total and ETA. The public charger lead is unresolved and is not an approved purchase. The Rs9,700 figure is a spending allocation, not a delivered quotation or a guarantee.

Production remains `HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false`. The 3.5 W optional-load increment and 6 Ah capacity are provisional until established for the physical system. Blank calibration worksheets remain blank; example data is synthetic. These settings are not silently changed by the audit.

## Conditions for claiming that the project works

1. Independently calibrated real sensor readings on the assembled board, with measured uncertainty and correct current direction.
2. Verified startup/default-off/reset/fault behavior and real supply rails with the selected fan, converter and USB arrangement.
3. Compatible pack/charger operation, a defensible capacity basis and current-boot charge reference; no BMS bypass or guessed full-charge synchronization.
4. Measured component temperatures and stable logging/control at the qualified operating loads.
5. Repeated physical baseline/priority trials with the same starting conditions and independent stopping criterion, reporting fan service lost as well as lamp service gained.
6. Updated academic claims, actual costs, secure assembly and reproducible code/CAD/data. Solar needs physical evidence if retained as a demonstrated final-project feature.

Only the optional fan is switched. The essential lamp remains powered, so the operator must stop trials at the normal reserve/operating endpoint. This design has no reverse-polarity blocking and is not a replacement for the purchased BMS. These specific boundaries remain in the assembly/test procedures.

The immediate next work is procurement confirmation and staged lab bring-up, not more speculative PCB layers or additional features. The full sequence and owner assignments are in [NEXT_STEPS.md](NEXT_STEPS.md).
