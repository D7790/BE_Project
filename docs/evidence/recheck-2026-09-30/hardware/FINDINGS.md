# Rev B hardware crosscheck — 30 September 2026

The current native design and fabrication package remain internally consistent. This is a CAD/document audit; no board, battery, converter or load has been physically tested. Native CAD, purchasing BOMs and the fabrication ZIP were not modified.

## Fresh checks

| Check | Result |
| --- | --- |
| KiCad 10.0.6 ERC, all configured severities including exclusions | 0 reported violations |
| KiCad DRC with zone refill in memory, all track errors, schematic parity | 0 reported geometric violations, 0 unconnected, 0 reported parity violations under the native configuration |
| Native schematic / PCB / design manifest / BOM | All 114 electrical pad assignments, 50 component locations and 19 nets agree; values, footprints and ordering codes agree |
| Independent critical mappings | INA219 SOIC-8 pins and addresses; MOSFET gate/source/drain; diode polarity; shunts, fuses, connectors and firmware GPIOs agree |
| Power routing | All 20 explicit front-copper power/return paths satisfy the documented minimum widths |
| Fabrication | All 12 freshly exported Gerber/job/drill files match the packaged versions after excluding timestamp metadata only |
| Archive | 15 unique entries, CRC pass, native source/track-audit hashes and included instructions match |
| Purchasing list | The grouped BOM expands to exactly the same 50 locations as the individual BOM |
| Mechanical geometry | 100 × 90 mm, four copper layers, 104 vias, 137 plated holes and four 3.2 mm unplated holes; terminal pitch 5.08 mm / drill 1.3 mm and C11 pitch 2 mm agree with the selected footprints |
| Internal planes | In1.Cu and In2.Cu each contain one connected filled GND polygon, approximately 8,529.15 mm², without routed internal signal/power tracks |
| Saved top preview | Visually inspected: connector labels/polarity, board revision and USB jumper warning are readable; this is not an actual-parts fit check |

## Additional check of previously ignored categories

The delivered project's five ignored DRC categories and the four ignored ERC categories were changed to warnings **only in `all-rules-scratch/`**. These scratch files are evidence, not a new released PCB revision.

With no categories ignored:

- DRC reports zero geometric violations and zero unconnected items.
- DRC schematic parity reports six `footprint_filters_mismatch` warnings for J1–J6.
- ERC reports the same six `footprint_filter` warnings.
- No errors or other warnings are reported.

The generic two-pin connector symbol has the pattern `Connector*:*_1x??_*`, which does not match the selected `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` library identifier. These are metadata-filter mismatches, not differences between the actual PCB and schematic footprint assignments. Each connector's two pin nets, BOM, pitch and drill pass the independent audit. The warnings remain explicitly documented; it would be inaccurate to call the all-rules ERC/parity run “zero warnings.” No native rule or footprint was changed to hide them.

## Electrical and project limits retained

- One custom sensor/control board is sufficient for the current project. The protected common-port 4S LiFePO4 pack/BMS, matched charger, 5 V converter and ESP32 remain purchased external units.
- The intended ceilings remain 2 A on the battery path and 1.5 A total continuous 5 V current, with starter lamp/fan branches measured at no more than 0.6 A each. Width continuity and four copper layers do not establish thermal ampacity.
- The 2 A near-pack DC fuse and disconnect are external. The board has no reverse-polarity blocking circuit. The essential lamp stays powered when the optional fan is shed, so discharge trials require the documented supervised normal endpoint.
- JP1 stays open for ordinary USB development. Battery-powered logging requires the exact ESP32 board's verified USB VBUS isolation. A power-only fan must not have an alternate ground/data return bypassing the low-side switch.
- Exact converter regulation/current-limit behavior, fan startup, fuse pulse suitability, part authenticity, physical footprint fit, calibration, component temperatures and runtime remain unmeasured.
- The ₹9,700 figure is an allocation ceiling, not a delivered quotation. PCB batch cost and remaining parts/charger compatibility are still unresolved. Solar and a PCB re-spin are not funded by that allocation.
- The original SIH PPT is historical and is already identified in `docs/NEXT_STEPS.md` as requiring scope/result corrections before use. No physical or publication claim should be inferred from that deck.

The next hardware milestone remains a battery-free assembled board whose sensor readings agree with an independent meter on a limited bench supply. Follow the native revision B assembly guide before adding the protected pack.

## Evidence

`verification.json` records input hashes and exact commands; `connectivity-audit.json`, `power-path-audit.json`, `erc.json`, `drc.json`, `all-rules-erc.json`, `all-rules-drc.json`, `drill-report.txt` and the fresh `gerbers/` directory provide the detailed outputs. `run_audit.py` reproduces these checks without saving the native board.
