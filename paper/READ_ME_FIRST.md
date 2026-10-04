# Wattsense research paper and next steps

Prepared 30 September 2026. This is a seven-page IEEE-style design-and-simulation draft with five original figures, two tables, four equations and nine references. It uses the four supplied authors in order. There are no measured hardware results, invented affiliations or publication-acceptance claims.

## Read and edit

- Paper: [PDF](../output/pdf/wattsense_research_paper.pdf).
- Editable Word: [DOCX](../output/docx/wattsense_research_paper.docx). Single-column editing layout, with native editable text, tables and four equations; all five original figures are embedded. Its 102 content checks pass, but Word rendering is unverified because the bundled document renderer is unavailable. The PDF retains the visually checked IEEE-style two-column layout.
- Readable editable manuscript: [wattsense-manuscript.md](wattsense-manuscript.md).
- Canonical editable content: [src/manuscript.json](src/manuscript.json). Edit this file before rebuilding; the Markdown and PDF are generated views.
- Original vector and high-resolution figures: [figures](figures), with captions, alt text and source hashes in `figure-provenance.json`.
- Project recheck: [evidence/recheck/FINDINGS.md](evidence/recheck/FINDINGS.md).
- Final paper package checks: [evidence/final-paper-audit.json](evidence/final-paper-audit.json).
- Limited wording/citation check: [evidence/originality-report.txt](evidence/originality-report.txt).

The newest whole-project audit is [30 September recheck](../docs/RECHECK_2026-09-30.md). Use it ahead of historical reports. The current package passes 48 technical checks including 96 actual manuscript/data comparisons. Changes include explicit Python-versus-host-C++ methods, consistent estimated-runtime notation, hash-bound build/visual QA, preserved authorship records and repaired PDF draft banners.

Word edits are independent of canonical JSON. If you revise the Word file, keep an edited copy; the generator will overwrite its output and does not import Word changes. The figure SVGs and plotting script remain separately editable.

The layout is IEEE-style rather than a named venue's approved template. Affiliation is intentionally omitted until supplied. Numerical displays say what was simulated and identify assumptions. The nominal lamp-service gain of 43.96% accompanies 54.47% less fan service; it is not a battery-capacity or equal-service efficiency improvement.

## What was checked

The fresh main suite passes 45 Python tests and 67 native C++ assertions, along with circuit/model runs. An independent publication recheck passed 38 checks before the separately recorded documentation-only corrections. A second manuscript review checked all prose and 18 numerical comparisons. The current draft-package checker verifies hashes, current evidence, figures, references, authors, numerical headlines and draft status. All seven final PDF pages were rendered and visually reviewed by the assistant; accountable author review remains pending.

Fresh KiCad ERC/DRC reports have zero reported violations, unconnected items and schematic-parity differences under the recorded rule settings. Four ERC and five DRC categories are ignored in those settings; see `evidence/recheck/ignored-cad-checks.csv`. No test result establishes physical safety or manufacturing qualification.

The latest scratch check enables those categories. It reports six connector footprint-filter warnings for J1–J6 in ERC and the corresponding six parity warnings in DRC. Actual assigned footprints, nets, pitch and drill checks match; there are no geometric/connectivity defects or other warnings in that scratch check. Details are in the latest whole-project audit.

The docs previously used the word "conservative" for the no-future-solar estimate. Six documentation files now correctly call it a heuristic. Nominal energy and omitted upstream losses prevent a minimum-runtime guarantee. No firmware, model, CAD or production flag was changed by this wording correction.

## Originality check and its limits

The local check found no exact eight-word overlap in the abstract and prose paragraphs against two complete papers and two very short source excerpts. It excludes figures, tables, equations and bibliography. The diagrams are original drawings from project data/topology. No manuscript was uploaded to an external checker.

This is not a plagiarism percentage, Turnitin/iThenticate report, exhaustive novelty search or certificate. Exact matching misses paraphrased copying, translation and many forms of idea overlap. Two papers were only available to the automated checker as one 18-word excerpt each. Full coverage and access failures are documented in `originality-report.txt`. Use the college's authorized institutional similarity service and inspect its matches before submission.

## Before submitting

1. Give the guide this draft and decide whether the target accepts simulation/design papers. The contribution is reproducible integration and design screening; priority shedding itself is established prior work. Hardware validation would make a final-project paper substantially stronger.
2. Supply college/university, department, author affiliations, corresponding author/email, actual contributions, funding/conflicts and any guide co-authorship justified by contribution. All authors should review the full manuscript and sources.
3. Choose a real conference/journal, inspect its scope and author instructions, then move the draft into its official template and page limit. No venue, APC payment or submission has been made.
4. Review the AI-assistance disclosure for that venue. The draft already states how Codex and Scientific Agent Skills were used. Keep the evidence and code accountable to the human authors.
5. Obtain the institutional similarity report. Resolve unattributed or misleading matches by source review and correct writing/citation, not by chasing a target percentage.
6. Decide what the submission actually claims. A simulation-only submission must keep the explicit assumptions and limitations. A hardware-results paper must first collect the measurements below; do not relabel these synthetic results as experiments.
7. After author/guide approval, archive shareable project code/data with an actual repository URL or DOI and verify rights/licences. There is no public data DOI yet. Local reference PDFs used for the overlap audit are not included in the review ZIP.

## Next engineering work

No parts have been purchased. Use the existing below-Rs10,000 procurement plan to select an actual protected 4S pack, compatible charger, converter, lamp/fan and PCB fabrication quote. Do not treat the spending allocation as a delivered quotation. The selected scope still uses one custom board, not a custom BMS.

Measure the converter and load terminals before qualifying a fan: the starter startup simulation reaches about 4.79 V on the common rail but 4.55 V at the fan. Verify actual allowable voltage, startup current and reset/restart behavior. Then follow the current-limited bring-up, sensor calibration and loaded thermal checks in `docs/LAB_START_GUIDE.md` and `docs/TEST_PLAN.md`.

For publication measurements, plan matched repeated baseline/priority trials with the same pack, initial charge, loads and stopping criterion; measure current/voltage independently and log both lamp and fan service, energy, temperatures and failures. The essential lamp is not automatically disconnected at the reserve endpoint: supervised physical trials need an external stop. Hardware arming remains disabled until the documented qualification is complete.

## Reproduce locally

From the project root, with the existing Windows environment:

```powershell
.\.venv\Scripts\python.exe simulations/run_all.py
.\.venv\Scripts\python.exe paper/src/make_figures.py
.\.venv\Scripts\python.exe paper/src/prepare_records.py
.\.venv\Scripts\python.exe paper/src/build_paper.py
.\.venv\Scripts\python.exe paper/evidence/originality_check.py
.\.venv\Scripts\python.exe paper/src/check_paper.py
```

PDF dependencies are pinned in `requirements-paper.txt`; the renderer uses Windows Times New Roman fonts. Core simulation setup is documented in the project README. KiCad/ngspice and the existing native compiler are required for the complete model/test suite. The local overlap check runs offline by default and depends on the retained audit corpus; the small review ZIP does not redistribute full reference texts.

Rendering alone does not complete visual QA. After editing, render all PDF pages with Poppler and inspect equations, captions, tables and all figures. `build-record.json` returns to awaiting-visual-QA on each build. The original `verify_evidence.py` compares against the historical September 28 checkpoint; documentation corrections intentionally change those old document hashes. Use `check_paper.py` for the current package and retain the historical checks plus `documentation-finalization.json` as the audit trail.

Record an actual completed review in `evidence/visual-review.json`, bound to the current PDF and page-render hashes. Never reuse an old review for a changed PDF. `check_paper.py` requires that record and current figure QA; its failure before review is intentional. `finalize_package.py` reruns checks and packages the draft but cannot grant visual or human approval. The separate Word record deliberately says `CONTENT_VALIDATED_RENDER_UNVERIFIED` until a real Word rendering is inspected.

The Scientific Writing skill was installed at `C:/Users/dhane/.codex/skills/scientific-writing`; it was read and used directly in this session. Restart Codex when needed for discovery as an installed skill in a later session. Source provenance and the verified arXiv attribution are retained in the evidence records. Its human-verification gates deliberately remain incomplete; a passing numeric/syntax check is not submission approval.
