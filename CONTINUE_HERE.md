# Wattsense — continuation checkpoint

Updated: 3 October 2026 after restoring the user's battery-mounted, battery-powered monitoring and advisory concept from the SIH proposal. No automatic continuation is scheduled.

## Latest checkpoint — read this first

### Battery-mounted monitor and guidance correction, 3 October 2026

- **Use `output/pptx/WattSense_Review_3_Battery_Centred_Final.pptx` for Review 3.** The user clarified the device is mounted near and powered by the battery, reporting remaining energy and runtime and recommending which optional loads to turn off. The previous AC-first expansion misrepresented the main idea. It is superseded, while household AC/DC support remains part of the corrected architecture.
- Re-read all original SIH slide text and its architecture image. Solar panel feeds a compatible charge controller OR AC mains feeds a matched AC-to-DC battery charger. Charging feeds the protected DC bus. Protected battery/BMS connects bidirectionally through appropriately rated whole-battery current sensing to that bus. The bus feeds DC loads via converters, AC loads via an inverter and WattSense via a regulated supply, so device/inverter demand is included. Power and information flows are separately labelled in the new editable block diagram.
- Signature recognition and user priorities support energy/runtime guidance. Start with 4–6 known AC/DC load states and UNKNOWN rejection, then mixtures. User turns off advised optional loads manually; no automatic mains switching or custom BMS is required. Net current during charging is not gross load demand. Default backup assumes no future charging; solar-supported estimates are conditional. Measured battery-side demand already includes conversion loss and monitor consumption.
- Exactly 14 slides. All 20 full paper titles and author/year cells, citations, confirmed rolls, Group 7, Mahesh Sapte and 3 October 2026 remain intact. Final SHA-256 `64d8063df43248a7fce6de2cea3113f67ec91abfefe6d9eeeb86161f83ea85fe`. All 14 final reimported slides visually inspected; 33 artifact/content checks pass, package and geometry zero findings/warnings. Independent content audit confirms accuracy, not physical hardware acceptance. Private evidence and builder: `.analysis/review3-battery-centred/`. PowerPoint desktop execution itself remains unverified.
- Latest scope authority is `docs/BATTERY_CENTRED_SCOPE.md`; README and the earlier expanded scope now point to this clarification. Existing Rev B remains an unbuilt low-power DC board (2 A battery path, 1.5 A continuous 5 V) and cannot carry household inverter current or connect to mains. Larger backup experiments require separate ratings/current sensing and compatible equipment. No code, CAD, physical hardware, trained model, measured data, purchases or historical simulation results changed.
- No delivery/affordability claim: budget stays below ₹10,000 but complete charging/inverter/metering equipment needs new quotes or borrowing. Battery chemistry, charger/controller, whole-current path and regulated monitor supply must be qualified before physical integration. The user presented an urgent 10-minute review deadline, so this correction prioritised the editable presentation and truthful concept.

### Expanded household AC and battery DC scope, 3 October 2026

- **Latest presentation: `output/pptx/WattSense_Review_3_Expanded_AC_DC_Checked.pptx`.** This supersedes the prior DC-only energy-signature presentations. The user explicitly requested household AC coverage and scope expansion. Current scope authority: [docs/EXPANDED_SCOPE_AC_DC.md](docs/EXPANDED_SCOPE_AC_DC.md). README now links this roadmap and deck; the earlier blueprint, next-step checklist and project-flow document carry dated supersession notices.
- **Main USP:** selected household AC appliance signatures and consumption estimation, supported by appropriately rated DC battery/UPS monitoring and backup-runtime estimation. Functional flow: AC meter -> ESP32/local Python features -> known/UNKNOWN output -> measured total and inferred appliance Wh -> dashboard; independent battery energy/demand -> runtime -> dashboard. The combined household acquisition and estimator are proposed additions, not current implementation.
- Start with **4–6 known appliance types**, one appliance per recording, varied operating states and repeated whole sessions. Compare a Random Forest candidate, Decision Tree and profile matching in local Python. Hold complete sessions apart for training/tuning/test; evaluate unseen/ambiguous loads. Controlled combinations and aggregate attribution follow individual-load validation. Slow meter telemetry does not establish raw AC waveform, harmonic or fast-transient features.
- Exactly **14 editable slides**, with the supplied college template's 4:3 size, logos and section order. All 20 full literature titles plus author/year retained; four small literature captions remain removed. Cover: Dhanesh 4114, Yash 4101, Mrudula 4212, Ujjwal 4154; Group 7, guide Mahesh Sapte, 3 October 2026. Updated problem, objectives, native architecture, dataset, evaluation, timeline and notes distinguish prepared DC foundation from proposed AC work.
- Final PPTX SHA-256 **`131fa2fae5e2205583046f3469a707e8b79cab4c976cf3f0c93f8eb364385e0f`**. All 14 final reimported slides rendered and individually inspected; all final PNGs match the repaired drafts. 83 content/link/package/hash checks pass; layout and package checks show zero findings/warnings. Native bullets on slides 2, 7 and 8 were repaired after finding export loss caused by shape-level `lineSpacing`. Private evidence: `.analysis/review3-expanded-ac-dc/`, including finalization receipt `validation-checked.json`, final crosscheck and independent content/engineering audits. Native PowerPoint desktop execution remains unverified.
- **Hardware boundary:** Rev B is an unbuilt non-isolated INA219 DC board, not an AC frontend. Its 2 A battery path and 1.5 A continuous 5 V ceilings remain subject to physical qualification. It cannot connect to household mains or carry household inverter battery current. A backup experiment requires separately rated whole-battery sensing or trustworthy compatible UPS telemetry with independently established usable energy. Bypassing an inverter around Rev B invalidates whole-pack current/SOC coverage. Do not pair the proposed LiFePO4 pack with an unverified lead-acid UPS charger.
- **Next build sequence:** qualify/quote or borrow a rated enclosed AC meter with a documented isolated data interface; add raw AC logging and independent calibration; collect appliance sessions and compare models; then qualify compatible backup equipment and validate Wh/runtime against matched references. Use real W, not apparent VA. Measured battery-side demand already includes inverter loss/idle; AC-derived predictions need a consistent loss model without double-counting.
- **Budget remains below ₹10,000, affordability not established.** The old ₹9,700 DC allocation excludes the new AC meter/interface and household backup equipment. Prioritise AC data collection, borrow lab/compatible UPS hardware, defer solar and unnecessary fabrication, then obtain a complete delivered quote before purchases.
- No production code, firmware, CAD, arming flags, dataset, simulation results or research paper changed. No AC acquisition, trained classifier, physical prototype, purchases or real measurements have been reported. Older paper/workbook/team-guide narratives require follow-up alignment before reuse; retain their historical DC evidence and avoid describing it as AC validation.

### Paper-title literature tables and confirmed rolls, 3 October 2026

- **Latest presentation: `output/pptx/WattSense_Review_3_Energy_Signature_Paper_Titles.pptx`.** This supersedes `WattSense_Review_3_Energy_Signature.pptx` for presenting. The previous file is preserved.
- User requested full research-paper titles together with author names and years inside the literature-review reference column. All 20 titles now appear in full across the same four five-paper native tables. Column widened, other cells kept concise and readable. No ellipses or title abbreviations. All other template columns retained; still exactly 14 slides.
- Removed all four small literature-topic captions below the survey tables at the user's request. Slide numbers remain. Confirmed and updated the cover and its notes: **Mrudula Pagar 4212, Ujjwal Kshirsagar 4154**. Dhanesh 4114, Yash 4101, Group 7 and Mahesh Sapte remain unchanged. These four roll numbers are now the current confirmed details; older copying guides/records retain their historical unknown placeholders.
- All 14 final imported slides rendered and individually inspected. Nine unaffected slides render byte-identically to the previous deck. Package and geometry checks show zero findings/warnings; all native tables remain editable, and full citations/reference notes remain unchanged. Final SHA-256 `faef170642b054f0b278ad0a175367809ab6849891cd66bb77896d121c556df0`. Private edit/validation/audit evidence in `.analysis/review3-literature-titles/`. Native PowerPoint desktop execution remains unverified.
- No underlying code, CAD, paper, dataset or simulation changed. The energy-signature development/physical-validation status remains as described below.

### Energy-signature Review 3 presentation, 3 October 2026

- **Latest presentation: `output/pptx/WattSense_Review_3_Energy_Signature.pptx`.** User clarified that energy signature and estimation are the USP. The new editable deck centres on measured load profiles, selected-load identification/UNKNOWN, load energy and battery-runtime estimates. The prior lamp/fan-priority presentation is historical.
- Exactly **14 slides**, using the supplied college template's 4:3 size, logos, headings and section order. Includes 20 literature papers across four native-table survey pages, an editable information-flow diagram, dataset/evaluation/timeline tables and full source notes. Five new signature papers were checked on primary publisher pages; battery/integration citations reuse the previously verified literature records.
- Cover: **Group 7, guide Mahesh Sapte, 3 October 2026**; Dhanesh 4114 and Yash 4101. Mrudula and Ujjwal roll numbers remain blank for user editing. No visible administrative confirmation reminders.
- All 14 final PPTX slides reimported, rendered and individually inspected. Package, geometry and font checks pass with **zero findings and zero warnings**. Final file SHA-256 `ba30be5cfb6617ba05229caa0c76ea31f79e115b2777a1c9e361eedcbd74b955`. Private evidence/builders: `.analysis/review3-signature/`; finalization receipt `validation-final.json`, visual/hash checks `final-crosscheck.json`, independent source audit `independent-content-audit.md`. PowerPoint desktop execution itself is unverified.
- **Implementation boundary:** this task changed presentation content only. Existing sensing/charge/runtime code, local dashboard, synthetic/model records and unbuilt Rev B CAD provide the foundation. No trained signature classifier, raw-rate recorder, physical dataset, new simulation or hardware validation was created. Nominal acquisition is 10 Hz but current JSON/CSV telemetry is approximately 1 Hz; qualify raw logging before signature collection. Start with 4–6 compatible known DC load types and separate recording sessions for testing; use UNKNOWN/ambiguous rejection. No universal AC recognition or classifier accuracy is claimed.
- **Next project alignment:** implement and evaluate the signature/data stage, then reconcile the main project guides, workbook title/content, README and research paper with this user-confirmed USP. Those older artifacts still describe the earlier priority-control scope and must not be presented as completed signature work. Preserve historical simulation results with their original scope. Hardware/solar arming flags remain false; no parts or physical measurements reported.

### Project workbook hard-copy content, 3 October 2026

- User supplied `Project_work _Book_AY_2026 Format.doc` and requested information to fill the hard copy. Extracted the legacy binary Word document read-only; original SHA-256 `fdcdfba70d6ad33adf33a1b0ca6c9853422717f6669fd3470167bcc70ba30e15` is preserved.
- **Confirmed latest team details: Group 7; guide Mahesh Sapte.** This supersedes the earlier tentative Chetna Jain guide name. Dhanesh 4114 and Yash 4101 are confirmed; Mrudula/Ujjwal roll numbers, personal contacts, TE results and guide designation/contact remain unknown.
- Copy guide: `output/pdf/WattSense_Project_Workbook_Copy_Guide.pdf` (10 visually reviewed pages). Editable text: `output/workbook/WattSense_Project_Workbook_Copy_Text.txt`. Covers actual workbook group fields, technical attachments, five literature rows and reference sheet, supported Sep/Oct logs, current Review 3 fields, future plan, competition and publication status.
- Technical and reference content independently reviewed against project evidence. Paragraph extraction checks and rendered-page hashes are in `.analysis/workbook/build_record.json`; builders and read-only source extraction are alongside it. Unknown ISSNs are explicitly pending verification rather than invented. Workbook PDF is a copying reference, not a filled/signed original form.
- July/August/early-September dates, previous staff feedback, prior review dates, SIH event/certificate details and awards are not known. Future completed-activity rows and staff comments/signatures stay for actual records. Review 3 completion has not been reported. The template repeats the final Sem 2 "Review 2" label; department confirmation is needed before renumbering.
- No code, CAD, paper, PPT or physical-testing status changed. Older presentation/title copies may still carry the tentative guide name; use Mahesh Sapte in current workbook details and future updates.

### Shareable teammate guides, 2 October 2026

- Start with `output/team-guide/00_READ_ME_FIRST.md`. Seven editable Markdown files explain the complete project, hardware/PCB, software/demo, simulation/testing, all 14 presentation slides/viva, and team tasks/budget/next steps.
- Share `output/WattSense_Team_Guide.zip`. It contains only the seven guides, with working sibling links and no external image dependencies. Teammates need the full project separately for code/CAD/PPT/raw data and runnable commands.
- Independently reviewed hardware, budget, control, simulation values and slide consistency against current sources. Corrected the test setup to install `requirements.txt` before unittest; clarified Python plant versus reduced ngspice execution, voltage-dependent startup demands, and separate dashboard versus priority runtime estimates.
- Documentation/package checks pass: seven files, nine sibling links, 46 referenced project paths, printed runtime values/percentages and seven budget allocations. ZIP entry bytes and CRC pass. Evidence: `.analysis/team-guide/validation.json`; repeatable documentation packaging script: `.analysis/team-guide/package_and_check.py`.
- No production code, CAD, presentation or paper changed; no hardware tests or software suite rerun for these guides. Latest full recorded technical audit remains 30 September. No parts or physical measurements reported; production hardware/solar flags remain false. Review 3 is 3 October 2026.

### Presentation annotation cleanup

- Latest deck: `output/pptx/WattSense_Review_3_14_Slides_Presentation.pptx`. User requested removing three visible notes: title-page details confirmation, timeline schedule condition, and reference-page speaker-note pointer. Removed these plus their title-page asterisk/dagger markers. User will correct roll numbers/guide details manually.
- Still exactly 14 slides. Original native chart XML, relationships and embedded Excel workbook were preserved byte-for-byte. All 11 untouched slides render identically to the checked deck; the three changed slides were visually reviewed. Notes and remaining scientific content are unchanged. Private edit and validation records: `.analysis/review3-ppt/cleanup-*` and `validation14-clean.json`.

### Exactly 14 slides, 1 October 2026

- Use `output/pptx/WattSense_Review_3_14_Slides_Checked.pptx` for Review 3. This supersedes the earlier 22-slide presentation and intermediate 14-slide export.
- All 14 template sections/slides remain in order, including four literature pages with 20 papers. PCB, control policy and architecture share slide 9; data and validation status share slide 10; simulated runtime and evaluation targets share slide 11. Full reference metadata remain in speaker notes.
- Independently crosschecked claims and references, verified native chart values against stored results, and rendered/inspected every slide after importing the final PPTX. Private evidence: `.analysis/review3-ppt/final14-crosscheck.json` and `validation14-checked.json`. PowerPoint desktop execution was not tested.
- Two temporary roll numbers and guide confirmation remain pending. No underlying software, CAD, simulation results or paper changed.

### Review 3 presentation, 1 October 2026

- Editable presentation: `output/pptx/WattSense_Review_3_03_Oct_2026.pptx`. It uses the supplied `Presentation format.pptx`, which remains unchanged. The 22-slide deck preserves the college's 4:3 format, covers all template sections, adds PCB/control/simulation evidence, and includes presenter notes and 20 literature references.
- Latest title-slide order: Dhanesh Chaudhari (4114), Yash Ahire (4101), Mrudula Pagar (4114* temporary), Ujjwal Kshirsagar (4101* temporary). Department: Electronics and Telecommunication Engineering. Review: 3 October 2026. Prof. Chetna Jain is shown with a confirmation marker because the user said "I guess"; confirmation remains pending. The research paper's author order was not changed.
- All 22 final imported slides were rendered and visually inspected. Native tables, two charts with editable workbook snapshots, and flow diagrams remain editable. Private finalization, literature provenance and visual review records are in `.analysis/review3-ppt/`. PowerPoint desktop execution itself was not tested.
- Slides distinguish software/CAD/model evidence from unbuilt hardware. They retain the lamp/fan service tradeoff, startup failures and provisional cost. No new hardware, simulation result, firmware setting, CAD file or manuscript changed for this presentation.
- Before presenting: replace the two temporary roll numbers, confirm the guide's name, and rehearse the existing simulated demo using `docs/REVIEW_DEMO.md`. Keep real hardware claims pending measured evidence.

### Repeated crosscheck and editable paper, 30 September 2026

- Read `docs/RECHECK_2026-09-30.md` and `paper/READ_ME_FIRST.md`. New independent audits are in `docs/evidence/recheck-2026-09-30/`; before-change paper/results snapshots remain there.
- Fresh 45 Python tests, 67 native C++ assertions and both firmware builds pass. 12,000 C++/Python state/output comparisons and 15 independent numerical checks pass. All 39 simulation CSVs reproduce byte-for-byte. Production code and arming flags unchanged.
- Native CAD/BOM/fabrication ZIP unchanged. Configured checks pass; scratch all-rules checks expose six generic connector footprint-filter warnings for J1–J6, mirrored in parity. Actual footprint assignments, nets, pitch/drills match; no geometric/connectivity defect. Do not claim all-rule zero warnings.
- Paper methods now explicitly distinguish Python plant/controller execution from host C++ tests; notation and a claim mapping corrected. Numerical checker compares actual prose/tables/PDF to data. Final draft checks 48/48, actual manuscript/data 96/96, nine artifact-regression tests and four negative-fixture checks pass. PDF build/visual QA are hash-bound; package creation no longer grants QA. Existing author/policy declarations survive rebuilds.
- Final PDF has seven visually reviewed pages; fixed missing draft banners on figure pages. `output/docx/wattsense_research_paper.docx` provides editable text/tables/native equations in a single-column layout; 102 content checks pass. Word visual rendering is unverified because bundled LibreOffice is absent. Never call that Word layout visually approved. Word edits are not automatically synced back into canonical JSON.
- Limited originality rerun remains zero exact eight-word overlaps in abstract/prose against two full papers plus two short excerpts; not institutional clearance. Author/guide review, venue/affiliations, institutional similarity and physical measurements remain pending. Updated review ZIP includes Word, PDF, original figure assets and audits. Nothing purchased, flashed or submitted.

### Research paper and publication audit, 30 September 2026

- Start with **`paper/READ_ME_FIRST.md`**. Seven-page IEEE-style draft: `output/pdf/wattsense_research_paper.pdf`; editable content `paper/src/manuscript.json`, readable version `paper/wattsense-manuscript.md`. Five original SVG/PNG figures and nine references. Authors: Dhanesh Chaudhari, Ujjwal Kshirsagar, Mrudula Pagar, Yash Ahire. Affiliation and venue remain unspecified; user confirms no hardware measurements.
- Fresh full suite passes 45 Python tests and 67 native C++ assertions. Independent recheck passed 38 checks, including fresh ERC/DRC and numerical comparisons. Paper-specific numeric review passes 18 comparisons. Current draft package checks: `paper/evidence/final-paper-audit.json`.
- Literature confirms prior priority-shedding work; the paper claims reproducible design/simulation integration, not a new algorithm or measured prototype. Nominal lamp service +43.96% accompanies fan service -54.47%. All startup failures and model assumptions are disclosed.
- Limited local originality check: no exact eight-word overlap in abstract/prose against two complete papers plus two short excerpts. Not a global plagiarism score or institutional certificate. Reports, coverage, scripts and human-review gaps are under `paper/evidence/`.
- Installed and used K-Dense Scientific Writing skill from Skills.sh; citation and AI assistance are disclosed. Literal isolated headless Chrome launch was blocked by automatic approval, so web work used the supported background browser and primary-source retrieval.
- Corrected misleading "conservative runtime" wording in six documentation files: the no-future-charge estimate is a heuristic, not a guaranteed lower bound. Production code, model, CAD, manufacturing ZIP and arming flags were unchanged. Preserve September 28 reports as historical snapshots; documentation-correction hashes are separately logged.
- Next: author/guide review; affiliations/declarations; target venue and official template; institutional similarity check. Hardware validation needs actual parts, calibration, startup/thermal captures and repeated matched trials before experimental publication claims. Nothing has been submitted or purchased.

### Final audit and finalized next steps, 28 September 2026

- Read **`docs/FINAL_AUDIT.md`** and **`docs/NEXT_STEPS.md`** first. The user requested one final whole-project audit and a concrete execution plan. Core remains Rev B four-layer PCB, three onboard INA219AIDR sensors, one switched fan, external classic ESP32/buck and purchased protected common-port 4S LiFePO4 pack/matched charger. No extra custom PCBs.
- Independent hardware, software and simulation reviews found no new material native-CAD or production-software defect. Fresh ERC/DRC/unconnected/parity all zero; exhaustive 50-location/114-pin/19-net audit and 20 explicit power paths pass. Fresh 12-file fabrication export matches the unchanged 15-entry ZIP except timestamps. Native CAD and ZIP unchanged.
- Final full suite passes **45 Python tests, 67 C++ assertions**, original/new SPICE and plant runs. Both firmware targets rebuilt successfully, same sizes as before. Independent algebra/quadrature/current-balance checks pass (15 checks; runtime agreement within 0.74 s). Model endpoint labels/stop tests now follow configured reserve/voltage rather than literals; current results unchanged.
- Corrected stale blueprint procurement/budget/module-carrier/extra-channel/persistence language; PCB_REQUIREMENTS ordering code and external-fuse distinction; and conflicting initial 5 V supply limits (unloaded J4 starts at 100 mA). Existing smaller-load guidance stays in force. Root README and validation docs point to the current audit and single next-step checklist.
- Current final evidence: `docs/evidence/final-audit-record.json` and `docs/evidence/final-audit/`. Prior crosscheck-record.json remains historical. The audit recorder is `.analysis/final-audit/record_final_audit.py`; it checks source hashes, build logs, archive and document links before writing the record.
- No physical tests, purchases, supplier messages/uploads or flashing. Exact converter/fan, compatible pack/charger, vendor DFM and delivered below-Rs10,000 total are still pending. Hardware/solar flags stay false. No new browser visual session; earlier UI evidence is historical, current code/HTTP/protocol checks passed.
- Original SIH PPT is unchanged and still contains unsupported AI/cloud/universal-appliance/custom-BMS claims; update it before presenting the revised project. The next-step checklist assigns four owners, immediate review preparation, staged procurement/bench/calibration/startup/thermal/runtime gates and final-semester deliverables. Confirm actual Review 3 date/rubric; do not assume PCB arrival before review.

### Hardware-performance simulation and project flow, 28 September 2026

- User asked to simulate hardware performance and explain project operation. Read `docs/HARDWARE_PERFORMANCE.md` and `docs/PROJECT_FLOW.md` first. Everything remains simulation/software/CAD evidence; no hardware or purchases.
- New `hardware_model.py`, `run_hardware.py`, `extract_copper.py`, `hardware-assumptions.json`, eight equation/energy-balance tests and `make_hardware_plots.py` are included in `run_simulations.ps1`. KiCad Python reads 20 actual F.Cu paths without editing CAD. The model includes assumed battery/OCV/wiring/converter behavior and known nominal component resistances; it is not a full electrochemical/PWM/BLDC/thermal/EMC simulation.
- Current suite: **45 Python tests and 67 C++ assertions**, nine original reduced circuits plus six new startup circuits, ideal/nonideal plants and plots. Latest execution/evidence is in `simulations/results/suite-summary.json` and `hardware-summary.json`. Earlier crosscheck-record.json is a historical checkpoint, not the hash manifest of these new files.
- Starter-load selection changed to approximately **2.5 W / 0.5 A class each**. A 3 W constant-power load can draw more than 0.6 A after drops. Actual measured per-branch ceiling remains 0.6 A; total 5 V continuous ceiling remains 1.5 A including ESP32. Updated active wiring/lab/buying notes. No new prices were checked.
- Nonideal starter case: 6 Ah, 68% to true 20% reserve, 90% efficiency, 2.5 W lamp + 2.5 W fan + 0.8 W controller: baseline lamp **5.4764 h**, priority **7.8836 h**, fan shed **2.4936 h** (~44% lamp extension at the expense of fan service). A separate 3 W case is retained for comparison with earlier ideal work, not as the starter recommendation.
- Eighteen paired sensitivity cases; 1 s versus 0.25 s runtime convergence within 0.75 s; conservation checks and analytical comparisons for six startup cases. Modeled large startup demand can collapse the common rail to ~2.995 V on a limited source; increasing assumed capacitance to 2200 uF does not fix sustained shortage. Even a higher-current source can fail the voltage screen due to path drop. PASS for the suite includes detecting these intentionally failing scenarios.
- All physical flags stay false. `config.h` only received a comment correction: the 3.5 W optional-load increment is provisional, not measured. Measure and replace it later. Main PCB, fabrication ZIP, protection/current limits and BOM are unchanged. Physical startup, thermal and fuse-pulse qualification remain required.
- New plots: `simulations/results/hardware-runtime.png`, `hardware-startup.png`, `hardware-losses.png` (SVG and raw CSV also saved). The basic live dashboard remains the earlier explicitly synthetic demo, not this accelerated electrical model.

### Full cross-check completed, 28 September 2026

- User requested a cross-check of all work. Read `docs/CROSSCHECK_REPORT.md` for findings, manufacturer references, evidence and remaining limits. This section supersedes earlier counts/build sizes below.
- Found and fixed C++ charge-accumulator precision loss at 10 Hz by using double precision; malformed JSON types that could kill the serial reader; acceptance of contradictory telemetry; charting unhealthy frames; duplicate calibration validation settings; possible raw-input overwrite; ambiguous capacity/reserve instructions; old 10 W load guidance; and USB/baseline-test wording.
- Current complete suite: **37 Python tests, 67 native C++ assertions** (16 locked + 27 armed policy + 24 register-reader), reduced SPICE and plant/fault runs PASS. Three added current cases test one hour at the actual 10 Hz cadence. Python tests include fake-serial recovery and calibration input preservation.
- Firmware builds: production RAM **22,164 B**, flash **323,053 B**; diagnostic RAM **21,960 B**, flash **303,189 B**. No flashing. Production hardware and solar flags remain false.
- Rev B ERC/DRC/parity/unconnected remain zero. Expanded checks cover all component footprint/value/BOM fields, firmware interface assignments, terminal pitch/drills and C11 pitch. A separate graph audit verifies **20 explicit F.Cu power/return paths** at documented widths. Native PCB/schematic/BOM geometry/circuit unchanged in this review.
- Manufacturing ZIP refreshed with 12 fabrication files, FABRICATION.md, SOURCE-VALIDATION.json and POWER-PATH-VALIDATION.json. `check_and_export.ps1` now reruns both audits before packaging.
- Desktop UI checked through the in-app browser on an isolated temporary server: normal, shedding, refused restore and fault display; no captured console warnings/errors. Screenshot: `docs/evidence/dashboard-fault-crosscheck.png`. Existing mobile tests remain historical; no new mobile claim.
- Active instructions now cap initial lamp/fan at 0.6 A each and total 5 V continuous loading at 1.5 A, including ESP32 if powered there. CAPACITY_AH is before reserve subtraction; partial Ah to 20% reserve is not total capacity. Real comparison uses MIN_H 0 vs MIN_H 3 with independently tracked common endpoint.
- No parts bought, no physical results, no price/ETA guarantees. Next remains exact-parts/quotes, mentor review, current-limited assembly, independent calibration, battery/charger qualification and measured thermal/runtime trials. Revision A is historical, not newly requalified; original SIH PPT remains unchanged.

### Latest continuation: procurement and lab tools, 28 September 2026

- User confirmed **no parts purchased** and **Pune 411048**. Four electronics students, college lab available, total budget below INR 10,000.
- New `hardware/BUYING_PLAN_PUNE.md` records dated public supplier leads and an INR 9,700 allocation ceiling, not a delivered quotation. Four-layer fabrication, all remaining components and a verified matched charger still need quotes. Solar is deferred/borrowed. `hardware/SUPPLIER_QUESTIONS.md` contains drafts only; no messages, uploads or orders were made.
- The browser-harness connection still timed out after the user enabled remote debugging. Public listings were checked using read-only web search instead. Do not repeatedly request the same browser permission.
- Revision B U1/U2/U3 now specify **INA219AIDR SOIC-8**, the active carrier variant; the old INA219AID tube code is obsolete per TI. Updated schematic/PCB values, manifest, BOMs, audit and exports. No geometric/routing changes. Native originals before this update are saved under `.analysis/revB-before-ordering-update/`. Revision A remains unchanged and would need this ordering-code update if chosen later.
- Refreshed KiCad checks: ERC 0, DRC 0, unconnected 0, parity 0; 114 pad assignments and all component values/order codes match. Latest four-layer ZIP is in the revision B `exports/` directory.
- New `bringup` firmware target holds GPIO25 LOW, scans all three INA219s and reports uncorrected readings, temperature and buttons. It ignores serial commands and is separate from dashboard telemetry. Build: `.\build_firmware.ps1 -Environment bringup`. Production remains `esp32dev`.
- Production measurement handling now checks every INA219 register transaction, signed decoding, calibration/configuration before and after reads, and overflow. No later successful read can hide an earlier transaction failure. These sequential reads are not atomic ADC snapshots.
- Latest full suite **PASS: 31 Python tests, 61 C++ assertions** (37 policy + 24 register-reader), nine reduced SPICE runs, plant/fault simulations and plots. Both firmware builds pass: production RAM 22,148 / flash 322,625 bytes; diagnostic RAM 21,960 / flash 303,189 bytes. No flashing. Both production hardware/solar flags remain false.
- New `wattsense/calibration.py` CLI, blank `calibration/measurements-template.csv`, labelled synthetic example/report and `docs/LAB_START_GUIDE.md`. Fits current gain/offset and voltage gain; validates held-out readings; never modifies firmware. No physical calibration data exists.
- Next: obtain actual delivered quotes, buy checked starter items, assemble/bring up on limited supplies, collect independent meter readings, then qualify the pack/charger and perform controlled-load and thermal/runtime experiments. Review 3 must not rely on unconfirmed delivery.

The following four-layer checkpoint is retained for design/simulation context; use the latest counts and files above.

- Current board candidate: **`hardware/pcb/wattsense-main-revB-4layer/wattsense-main.kicad_pro`**. The original revision A directory is preserved as the two-layer budget alternative.
- Revision B: four copper layers (signals/power / GND / GND / signals), 100 x 90 mm, 1.6 mm nominal, 1 oz outer / 0.5 oz inner copper, 104 through vias including 57 new GND stitching vias. Two internal GND fills are each a single connected polygon. No increase in the 2 A battery-path or 1.5 A continuous 5 V limits.
- Simulation-driven circuit change: R4/R5 are 2.2 kOhm on B; R6 remains 4.7 kOhm. At assumed 400 pF, the new pullups simulate 746 ns rise time, versus 1593 ns for A's 4.7 kOhm. Do not mix BOMs.
- B validation: ERC 0, DRC 0, unconnected 0, parity 0; independent audit passes 114 pad assignments. Fabrication ZIP includes all four copper layers: `exports/wattsense-main-revB-4layer-prototype.zip`.
- Software: **24 Python tests and 37 native C++ assertions pass**. Production controller header tested in separate locked/armed host copies. Real `HARDWARE_CONFIRMED` remains false.
- Fixed simulator voltage/current policy mismatch, invalid restore input handling, interrupted shedding-timer history and C++ floating-point delay at the three-second threshold.
- ESP32 rebuild passed: RAM 22,148 bytes, flash 323,245 bytes; no flashing.
- Added reproducible suite: `run_simulations.ps1`, `simulations/README.md`, scripts, nine reduced ngspice circuits, CSVs, PNG/SVG figures and source-hashed summaries in `simulations/results/`.
- Full report: **`docs/SIMULATION_REPORT.md`**. Ideal-model essential-load runtime: 4.879 h baseline vs 7.247 h priority, fan shed at 1.880 h; these are synthetic values, not a physical experiment. Nine capacity/efficiency pairs, seven fault cases and a capacity/current-offset error example are included.
- ngspice 46 is supplied by installed KiCad. Matplotlib 3.10.8 is in `.venv`; `requirements-simulation.txt` records it. The project-local PlatformIO cache now also contains `toolchain-gccmingw32@1.50100.0` for host tests; temporary armed copies/binaries are in `.local/host-policy-tests/`, not production firmware.
- Board top/isometric previews and simulation charts were visually reviewed. Final code, checks, assembly/BOM notes and handoff files are saved.

Next: obtain delivered quotes and verify exact purchased parts, choose B or A within the below-INR-10,000 total, prepare the honest Review 3 evidence, then assemble and test on a current-limited lab supply. No parts purchased, no board fabricated and no physical performance/thermal/EMC/protection results exist. Do not describe the simulations as hardware verification.

The sections below retain the 27 September baseline context. Where details differ, use the current revision B report and files above.

## Project and constraints

**Wattsense: Battery Monitoring and Priority Load Control for Small Solar Systems.** Four final-year electronics engineering students, total hardware budget below INR 10,000, with access to a college electronics lab, multimeter and adjustable power supply. Nothing has been purchased or assembled yet. Review 3 was described as five days away; final submission is next semester.

The original rough SIH presentation, `sih 2026 shubham.pptx`, remains unchanged. Scope changes were authorized. This can be a suitable final-year project if the team demonstrates real electronics, sensor calibration, fault handling and measured runtime comparisons. A dashboard and simulation alone are insufficient evidence of a completed electronics project.

## Completed and saved

- Project blueprint, system architecture, budget planning, reference wiring, review demonstration guide and test plan.
- Python backend and browser dashboard, with an explicitly labelled simulator and a separate USB serial hardware mode. Includes voltage/current/temperature monitoring, charge estimation, runtime above reserve, priority load shedding and CSV logging.
- ESP32 firmware for three INA219 sensors, DS18B20, optional fan switching and local buttons. Firmware compiled successfully; it has not been flashed or tested on hardware.
- One integrated custom KiCad main board, including native editable schematic, routed PCB, project, custom symbols, BOMs, assembly instructions, schematic PDF, board previews and a prototype fabrication ZIP.

No additional custom BMS, charger or converter PCB is required for the chosen scope. The intended system uses a purchased protected 4S LiFePO4 pack with its BMS, matched charger/controller, external regulated 5 V converter and external ESP32 development board.

## Where to resume

Start with `README.md` and `WATTSENSE_PROJECT_BLUEPRINT.md`.

- Software demo: double-click `run_demo.cmd`, then open `http://127.0.0.1:8765`.
- Review preparation: `docs/REVIEW_DEMO.md` and `docs/TEST_PLAN.md`.
- Firmware setup: `firmware/README.md`; build with `build_firmware.ps1`.
- KiCad project: `hardware/pcb/wattsense-main/wattsense-main.kicad_pro`.
- PCB overview: `hardware/pcb/wattsense-main/README.md`.
- Parts: `hardware/pcb/wattsense-main/BOM-grouped.csv` and `BOM.csv`.
- Assembly and staged testing: `hardware/pcb/wattsense-main/ASSEMBLY_AND_BRINGUP.md`.
- Design decisions: `hardware/pcb/wattsense-main/DESIGN_NOTES.md`.
- Fabrication guidance: `hardware/pcb/wattsense-main/FABRICATION.md`.
- Fabrication package: `hardware/pcb/wattsense-main/exports/wattsense-main-revA-prototype.zip`.
- Validation records: `docs/VALIDATION.md`, PCB `reports/VALIDATION.md` and `reports/connectivity-audit.json`.

The dashboard and KiCad were left open at the end of design work. Their saved files are independent of whether those processes remain running.

## Last completed validation

- 19 Python tests passed; JavaScript syntax and desktop/mobile dashboard presentation checked.
- ESP32 PlatformIO build succeeded: RAM 22,148 / 327,680 bytes; flash 323,097 / 1,310,720 bytes. Two nonfatal upstream OneWire warnings remain.
- KiCad 10.0.6 ERC: zero reported violations.
- PCB DRC: zero errors/warnings, zero unconnected items and zero schematic parity violations.
- Independent connectivity audit matched all 114 electrical pads across schematic, PCB and design manifest; additional pin mapping assertions passed.
- Schematic, board and assembly previews visually reviewed. Gerber/drill exports and fabrication ZIP integrity checked.

These are software/CAD checks, not physical validation. No fabricated board, assembled circuit, battery test, thermal test or measured performance result exists yet.

## PCB revision A essentials

- 100 x 90 mm, two layers, 1.6 mm FR4, 1 oz copper; 50 component locations, 19 nets and 47 vias.
- Three INA219AID SOIC-8 sensors at 0x40 (battery), 0x41 (converter input), 0x44 (charger output); 0.1 ohm shunts.
- AO3400A low-side fan switch, SS14 flyback diode, SMBJ15A TVS and Littelfuse 466-series 1206 fuses.
- Phoenix 1715721 terminal footprint. Verify actual ordered parts against the final BOM; similar-looking parts may have different footprints.
- Battery path design ceiling: 2 A. Total continuous 5 V load ceiling: 1.5 A. Initial lamp and fan each at or below 0.6 A, with actual startup and thermal performance still to be tested.
- J2 accepts the output of one matched charger/controller, never a raw solar panel.
- Use a common-port protected battery pack and an external near-pack fuse/disconnect. Separate-port packs require a revised harness.
- Keep JP1 open while powering the ESP32 through USB. Fan return is switched and must not receive a second ground connection.
- Firmware defaults remain `HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false`. Follow the bring-up guide before changing them. Only label charger input as solar when an actual solar controller is used.

## Next session priorities

1. Review actual component availability, footprints and delivered prices before ordering. The earlier INR 9,500 module-based estimate does not confirm that this custom-PCB version fits below INR 10,000. Do not buy three INA219 modules and a separate driver if assembling this PCB.
2. Confirm exact protected battery, charger, converter, ESP32 board, lamp and fan specifications. Consider battery-only demonstration first and borrowing or deferring solar hardware to stay within budget.
3. Plan procurement and assembly around Review 3. PCB delivery must not be assumed within the review deadline. Present CAD and software simulation honestly as current progress.
4. Perform staged lab bring-up, sensor calibration, current/temperature checks, load-shedding tests and measured baseline-versus-controlled runtime trials after hardware is available.

## Preserve this work

The native KiCad files are the editable design deliverables. Construction helpers such as `tools/generate_design.py` and `tools/route_board.py` overwrite design files; do not rerun them over manual edits. After design edits, run the PCB `check_and_export.ps1` script to refresh checks and manufacturing outputs. Old clean reports do not validate subsequent changes.

The firmware build uses the local virtual environment and a verified short junction at `C:\Users\dhane\.ws-pio` to avoid Windows compiler path-length problems. `build_firmware.ps1` handles this setup.

No purchasing, fabrication order, payment or physical validation has been performed. Resume from these saved artifacts rather than rebuilding the project from scratch.
