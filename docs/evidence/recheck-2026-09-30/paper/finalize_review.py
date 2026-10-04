"""Record resolution of the independent paper review after the final rebuild."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
m = read("paper/src/manuscript.json")
blocks = {block["id"]: block for block in m["blocks"] if "id" in block}
figure_code = (ROOT/"paper/src/make_figures.py").read_text(encoding="utf-8")
new_check = ROOT/"paper/src/check_manuscript_data.py"
spec = importlib.util.spec_from_file_location("data_check", new_check)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
negative = module.self_test(ROOT)
resolutions = [
    {"finding": "PAPER-01", "resolved": "Python reference controller" in blocks["C019"]["text"] and "not firmware-in-the-loop" in blocks["C019"]["text"], "detail": "C019 identifies the Python plant/control experiment and separately host-tested production C++ logic."},
    {"finding": "PAPER-02", "resolved": "T_hat" not in json.dumps(m) and "E_hat" not in json.dumps(m) and "T̂" not in figure_code, "detail": "Canonical notation is E_est/T_est; the regenerated Figure 2 was visually re-inspected and its subscript is legible."},
    {"finding": "PAPER-03", "resolved": "E103" in blocks["C004"]["evidence"], "detail": "C004 now links local model evidence as well as the literature source."},
    {"finding": "PAPER-04", "resolved": new_check.exists() and negative["status"] == "PASS", "detail": "New reusable actual-manuscript/data comparator detects wrong table values, wrong abstract percentage and stale PDF prose. Its report is separate from the scientific-writing registry check."},
]
record = {
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "PASS_RESOLVED" if all(item["resolved"] for item in resolutions) else "REVIEW_REQUIRED",
    "resolutions": resolutions,
    "automated_manuscript_comparisons": read("paper/evidence/manuscript-data-audit.json")["passed"],
    "independent_readonly_comparisons": read("docs/evidence/recheck-2026-09-30/paper/independent-paper-review.json")["passed"],
    "negative_fixture_tests": negative,
    "inspected_sha256": {path: sha(path) for path in ["paper/src/manuscript.json", "output/pdf/wattsense_research_paper.pdf", "paper/src/check_manuscript_data.py", "paper/figures/fig2_control_flow.png"]},
    "assistant_figure_review": "The final Figure 2 PNG was visually re-inspected; no clipping, overlap or missing subscript glyph was found. Other four figures were inspected earlier in this recheck.",
    "prior_evidence": "independent-paper-review-before-final-build.json preserves the intermediate comparison before the current PDF was regenerated.",
    "remaining_gates": "Human verification/author approvals, venue/template requirements, institutional similarity review and physical measurements remain incomplete. No submission or hardware qualification is claimed.",
}
(OUT/"paper-review-resolutions.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"status": record["status"], "resolved": sum(item["resolved"] for item in resolutions), "negative_tests": negative}, indent=2))
