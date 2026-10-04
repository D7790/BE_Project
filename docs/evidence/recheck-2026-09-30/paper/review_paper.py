"""Read-only substantive paper crosscheck; writes only beside this audit script."""
from pathlib import Path
import csv
import datetime
import hashlib
import html
import json
import re
import unicodedata
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()

def csv_rows(relative):
    with (ROOT / relative).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def norm(text):
    for a, b in [("E_hat", "Eest"), ("T_hat", "Test")]:
        text = text.replace(a, b)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = unicodedata.normalize("NFKD", text)
    return "".join(c.casefold() for c in text if c.isalnum())

m = read_json("paper/src/manuscript.json")
hw = read_json("simulations/results/hardware-summary.json")
fig = read_json("paper/figures/figure-provenance.json")
pdf = PdfReader(ROOT / "output/pdf/wattsense_research_paper.pdf")
pdf_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
pdf_text = re.sub(r"WATTSENSE \| DESIGN AND SIMULATION STUDY \| WORKING DRAFT\s*\d+", "", pdf_text)
normal_pdf = norm(pdf_text)
checks = []

def check(name, condition, detail=None):
    checks.append({"check": name, "pass": bool(condition), "detail": detail})

check("Hardware outcomes remain simulation only", hw["hardware_tested"] is False)
check("Four supplied authors preserved", m["authors"] == ["Dhanesh Chaudhari", "Ujjwal Kshirsagar", "Mrudula Pagar", "Yash Ahire"])
check("No invented affiliation", m["affiliation"] is None)
paragraphs = [("abstract", m["abstract"])] + [(b["id"], b["text"]) for b in m["blocks"] if b["type"] == "p"]
for cid, prose in paragraphs:
    check(f"Rendered PDF contains canonical paragraph {cid}", norm(prose) in normal_pdf)

b, p = hw["baseline"], hw["priority"]
bh, ph, fh = b["runtime_to_common_endpoint_h"], p["runtime_to_common_endpoint_h"], p["fan_service_h"]
gain = 100 * (ph / bh - 1)
loss = 100 * (1 - fh / bh)
for label, value in [("baseline hours", bh), ("priority hours", ph), ("fan hours", fh)]:
    check(f"Abstract rounds {label} correctly", f"{value:.3f}" in m["abstract"], value)
check("Abstract discloses lamp gain and fan loss", f"+{gain:.2f}%" in m["abstract"] and f"-{loss:.2f}%" in m["abstract"], {"lamp_gain_pct": gain, "fan_loss_pct": loss})
table = next(x for x in m["blocks"] if x["type"] == "table" and x["number"] == "II")
expected = [
    [f"{bh:.4f}", f"{ph:.4f}"],
    [f"{bh:.4f}", f"{fh:.4f}"],
    [f"{bh*(b['lamp_delivered_w']+b['fan_delivered_w']):.4f}", f"{ph*p['lamp_delivered_w']+fh*p['fan_delivered_w']:.4f}"],
    [f"{b['delivered_energy_wh']:.4f}", f"{p['delivered_energy_wh']:.4f}"],
    [f"{b['chemical_energy_wh']:.2f}", f"{p['chemical_energy_wh']:.2f}"]]
for row, wanted in zip(table["rows"], expected):
    check(f"Table II recomputed {row[0]}", row[1:] == wanted, {"actual": row[1:], "expected": wanted})

base_trace = csv_rows("simulations/results/hardware-runtime-baseline.csv")
priority_trace = csv_rows("simulations/results/hardware-runtime-priority.csv")
for label, rows, end in [("baseline", base_trace, bh), ("priority", priority_trace, ph)]:
    check(f"{label} endpoint matches raw trace", abs(float(rows[-1]["time_s"])/3600-end) < 1e-12)
    check(f"{label} endpoint crosses true SOC reserve", float(rows[-1]["true_soc_pct"]) <= 20)
first_off = next(row for row in priority_trace if row["state"] == "PRIORITY")
check("Fan shedding time matches raw state transition", abs(float(first_off["time_s"])/3600-fh) < 1e-12)
sweep = csv_rows("simulations/results/hardware-runtime-sensitivity.csv")
check("All 18 sensitivity pairs retained", len(sweep) == 18)
check("Every paired scenario reports both-load and priority service", all(float(r["priority_h"]) > float(r["baseline_h"]) for r in sweep))
prose = {b["id"]: b["text"] for b in m["blocks"] if b["type"] == "p"}
check("C025 states both numerical service changes", all(v in prose["C025"] for v in [f"{ph-bh:.4f} h", f"{bh-fh:.4f} h", f"+{gain:.2f}%", f"-{loss:.2f}%"]))
heuristic = 6 * 12.8 * (float(first_off["estimated_soc_pct"])-20) / 100 / float(first_off["load_sensor_w"])
remaining = bh - fh
check("C027 heuristic and counterfactual recomputed from shedding trace", all(v in prose["C027"] for v in [f"{heuristic:.4f} h", f"{remaining:.4f} h", f"{(heuristic-remaining)*3600:.0f} s"]), {"heuristic_h": heuristic, "counterfactual_h": remaining, "overestimate_s": (heuristic-remaining)*3600})
dc = next(r for r in hw["dc_cases"] if r["case"] == "starter_2_5W_each")
for key in ["output_a", "battery_a", "rail_v", "lamp_v", "fan_v", "converter_loss_w", "output_path_loss_w", "two_shunts_loss_w"]:
    check(f"C028 reported {key} matches DC result", f"{dc[key]:.4f}" in prose["C028"], dc[key])
for key in ["baseline_h", "priority_h"]:
    values = [float(r[key]) for r in sweep]
    check(f"C029 {key} range from all 18 pairs", f"{min(values):.4f}-{max(values):.4f} h" in prose["C029"])
err = read_json("simulations/results/system-summary.json")["capacity_and_offset_error"]
independent_error = 100*err["hours"]*(err["true_discharge_A"]/err["true_capacity_Ah"]-err["measured_discharge_A"]/err["configured_capacity_Ah"])
check("C029 seven-percentage-point example independently recomputed", f"{independent_error:.1f} percentage-point" in prose["C029"])
startup = hw["startup_cases"]
check("Three startup cases fail the stated 4.75 V rail criterion", sum(r["min_rail_v"] < 4.75 for r in startup) == 3 and "Three startup cases fail" in m["abstract"])
for n, key, cid, dp in [(2,"min_rail_v","C030",3),(4,"min_rail_v","C030",3),(5,"min_rail_v","C031",4),(5,"min_fan_terminal_v","C031",4)]:
    check(f"{cid} reported startup S{n+1} {key}", f"{startup[n][key]:.{dp}f} V" in prose[cid])
for i, result in enumerate(hw["convergence_checks"]):
    check(f"C034 convergence result {i+1}", f"{result['runtime_difference_s']:.2f}" in prose["C034"])
spice = read_json("simulations/results/spice-summary.json")
for resistance in [2200, 4700]:
    row = next(r for r in spice["cases"] if r["case"] == f"I2C rise with {resistance} ohm at 400 pF")
    check(f"C032 I2C {resistance} ohm rise time", f"{row['rise_30_70_ns']:.0f} ns" in prose["C032"])
check("C032 shunt loss independently calculated", all(v in prose["C032"] for v in [f"{2**2*0.1:.1f} W", f"{2*2*0.1:.1f} V", f"{2*2**2*0.1:.1f} W"]))
originality = read_json("paper/evidence/originality-report.json")
check("Originality claim is bounded, with no certification", "Not a plagiarism certificate" in originality["limits"][0])
check("Originality scope explicitly excludes captions/tables/equations", all(word in originality["draft_scope"] for word in ["equations", "tables", "figure captions"]))
check("Originality corpus is exactly two full sources and two 18-word excerpts", len(originality["source_coverage"]) == 4 and sum(s["normalized_words"] == 18 for s in originality["source_coverage"]) == 2)
check("No source reports physical validation of Wattsense", all("measured Wattsense" not in ref["text"] for ref in m["references"]))
auth = read_json("paper/evidence/authorship.json")
check("Author approval not fabricated", auth["accountability"]["all_authors_approved"] is False and auth["ai_use"]["human_verification_complete"] is False)

captured = ["paper/src/manuscript.json", "output/pdf/wattsense_research_paper.pdf", "paper/src/make_figures.py", "paper/src/build_paper.py", "firmware/include/controller.h", "firmware/src/main.cpp", "simulations/run_hardware.py", "simulations/hardware_model.py", "simulations/results/hardware-summary.json", "paper/evidence/literature-review.txt", "paper/evidence/originality-report.json"]
record = {
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "PASS_READ_ONLY_SUBSTANTIVE_CHECKS" if all(c["pass"] for c in checks) else "REVIEW_REQUIRED",
    "scope": "Independent local manuscript/PDF/prose, key result arithmetic, raw trace, diagrams and disclosure review. Does not re-open remote reference sources or certify plagiarism/hardware/publication readiness.",
    "checks": checks,
    "passed": sum(c["pass"] for c in checks),
    "total": len(checks),
    "pdf_pages": len(pdf.pages),
    "inspected_sha256": {path: sha(path) for path in captured},
    "figure_review": {"method": "Visually inspected all five current 300-dpi PNGs; compared flowchart to firmware controller.h and topology to reference wiring.", "scientific_content": "All 18 paired scenarios and all six startup cases retained; limitations, failed rail screens, fan service loss and omitted paths are disclosed.", "human_review_pending": True},
    "recommendations": [
        {"id": "PAPER-01", "priority": "medium", "type": "methods clarity", "location": "paper/src/manuscript.json C024; simulations/run_hardware.py:16,86,102", "finding": "The coupled plant executes wattsense.model.Controller, while C++ policy is separately host-tested. Manuscript does not explicitly name this separation.", "action": "Add one sentence naming the Python reference controller and separate C++ host checks; state that no firmware-in-loop or ESP32 execution is represented."},
        {"id": "PAPER-02", "priority": "low", "type": "notation consistency", "location": "paper/src/build_paper.py clean(); paper/src/make_figures.py Figure 2; manuscript equations 2-3", "finding": "Canonical text uses E_hat/T_hat, PDF translates those to E_est/T_est, while Figure 2 retains hatted T.", "action": "Use E_est/T_est consistently in canonical text, PDF and Figure 2; preserve meaning and regenerate evidence."},
        {"id": "PAPER-03", "priority": "low", "type": "claim binding", "location": "paper/src/manuscript.json C004", "finding": "C004 maps only to literature E001, although its final sentence draws an inference about the project's shared plant/estimator inputs.", "action": "Add local model evidence E103 to C004 to make the mixed-source paragraph traceable."}
        ,{"id": "PAPER-04", "priority": "medium", "type": "verification coverage", "location": "paper/src/prepare_records.py:92-96", "finding": "Consistency registry copies each summary value twice into Results and Evidence registry; its pass checks duplicated records rather than actual manuscript numbers.", "action": "Bind Table II, results prose and abstract values to current simulation evidence with parsed numeric checks. The read-only audit here performs such direct checks; the skill checker is still a registry check only."}
    ],
    "legitimate_pending_gates": ["No hardware measurements or parts purchased", "Human source/claim verification", "Author affiliations, contributions, approval and corresponding author", "Venue/template and disclosure-policy review", "Institutional similarity review; the two full papers plus two excerpts are only bounded wording evidence"],
    "new_web_requests": 0,
}
(OUT / "independent-paper-review.json").write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(json.dumps({"status": record["status"], "passed": record["passed"], "total": len(checks), "failed": [c["check"] for c in checks if not c["pass"]]}, indent=2))
