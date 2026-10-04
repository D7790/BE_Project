"""Compare actual draft prose/tables with saved simulation data and rendered PDF.

This is an offline data-consistency check, not physical validation, source approval,
similarity certification or author approval. --self-test mutates in-memory copies
only and does not write either the manuscript or production audit report.
"""
from pathlib import Path
import argparse
import copy
import csv
import datetime
import hashlib
import html
import json
import re
import sys
import unicodedata
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATHS = [
    "paper/src/manuscript.json", "output/pdf/wattsense_research_paper.pdf",
    "paper/figures/figure-provenance.json", "simulations/hardware-assumptions.json",
    "simulations/results/hardware-summary.json", "simulations/results/system-summary.json",
    "simulations/results/spice-summary.json", "simulations/results/hardware-runtime-baseline.csv",
    "simulations/results/hardware-runtime-priority.csv",
    "simulations/results/hardware-runtime-sensitivity.csv",
    "paper/src/check_manuscript_data.py",
]


def read_json(root, relative):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(root, relative):
    with (root / relative).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def normalized_text(text):
    # Source underscore names and PDF subscripts represent the same notation.
    # Compatibility with the prior draft lets historical audits still run.
    for before, after in [("E_hat", "Eest"), ("T_hat", "Test"),
                          ("E_est", "Eest"), ("T_est", "Test")]:
        text = text.replace(before, after)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = unicodedata.normalize("NFKD", text)
    return "".join(char.casefold() for char in text if char.isalnum())


def audit(root=ROOT, manuscript=None):
    """Return an audit without writing files; optional manuscript is a test fixture."""
    m = read_json(root, "paper/src/manuscript.json") if manuscript is None else manuscript
    hw = read_json(root, "simulations/results/hardware-summary.json")
    assumptions = read_json(root, "simulations/hardware-assumptions.json")
    figures = read_json(root, "paper/figures/figure-provenance.json")
    pdf = PdfReader(root / "output/pdf/wattsense_research_paper.pdf")
    page_text = []
    for index, page in enumerate(pdf.pages, 1):
        content = (page.extract_text() or "").replace("WATTSENSE | DESIGN AND SIMULATION STUDY | WORKING DRAFT", "")
        # Remove only this page's terminal footer, irrespective of overlay order.
        content = re.sub(r"\n" + str(index) + r"\s*$", "", content)
        page_text.append(content)
    text = "\n".join(page_text)
    rendered = normalized_text(text)
    checks = []

    def check(name, condition, detail=None):
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    def contains(cid, wanted, name):
        check(name, all(value in prose[cid] for value in wanted), {"claim_id": cid, "expected": wanted})

    check("source simulation completed", hw.get("status") == "CHECKS_PASS")
    check("performance is marked as simulation only", hw.get("hardware_tested") is False)
    check("rendered PDF contains author names in source order",
          normalized_text(", ".join(m["authors"])) in rendered)
    paragraphs = [("abstract", m["abstract"])] + [(block["id"], block["text"])
                  for block in m["blocks"] if block["type"] == "p"]
    for cid, paragraph in paragraphs:
        check(f"PDF contains canonical paragraph {cid}", normalized_text(paragraph) in rendered)
    prose = {block["id"]: block["text"] for block in m["blocks"] if block["type"] == "p"}

    baseline, priority = hw["baseline"], hw["priority"]
    bh, ph, fh = baseline["runtime_to_common_endpoint_h"], priority["runtime_to_common_endpoint_h"], priority["fan_service_h"]
    gain = 100 * (ph / bh - 1)
    loss = 100 * (1 - fh / bh)
    for label, value in [("baseline hours", bh), ("priority hours", ph), ("fan hours", fh)]:
        check(f"abstract rounds {label} correctly", f"{value:.3f}" in m["abstract"], value)
    check("abstract discloses calculated lamp gain and fan loss",
          f"+{gain:.2f}%" in m["abstract"] and f"-{loss:.2f}%" in m["abstract"],
          {"lamp_gain_pct": gain, "fan_loss_pct": loss})
    table = next(block for block in m["blocks"] if block["type"] == "table" and block["number"] == "II")
    expected = {
        "Lamp service (h)": [f"{bh:.4f}", f"{ph:.4f}"],
        "Fan service (h)": [f"{bh:.4f}", f"{fh:.4f}"],
        "Lamp + fan energy (Wh)": [f"{bh*(baseline['lamp_delivered_w']+baseline['fan_delivered_w']):.4f}",
                                   f"{ph*priority['lamp_delivered_w']+fh*priority['fan_delivered_w']:.4f}"],
        "All loads incl. controller (Wh)": [f"{baseline['delivered_energy_wh']:.4f}", f"{priority['delivered_energy_wh']:.4f}"],
        "Chemical energy (Wh, approx.)": [f"{baseline['chemical_energy_wh']:.2f}", f"{priority['chemical_energy_wh']:.2f}"],
    }
    actual = {row[0]: row[1:] for row in table["rows"]}
    check("Table II has exactly five distinct expected metrics", len(table["rows"]) == 5 and set(actual) == set(expected))
    for metric, wanted in expected.items():
        check(f"Table II data: {metric}", actual.get(metric) == wanted,
              {"actual": actual.get(metric), "expected": wanted})

    table1 = next(block for block in m["blocks"] if block["type"] == "table" and block["number"] == "I")
    rows1 = {row[0]: row[1] for row in table1["rows"]}
    table1_expected = {
        "Capacity / initial SOC": f"{assumptions['capacity_ah']:g} Ah / {assumptions['initial_soc_pct']:g}%",
        "Endpoint / time step": f"{assumptions['reserve_pct']:g}% / {baseline['integration_step_s']:g} s",
        "Lamp / fan delivered power": f"{assumptions['starter_lamp_w']:g} / {assumptions['starter_fan_w']:g} W",
        "Controller demand": f"{assumptions['controller_and_sensors_5v_w']:g} W",
        "Converter efficiency": f"{100*assumptions['converter_efficiency']:g}% fixed",
        "Battery/BMS resistance": f"{assumptions['battery_and_bms_resistance_ohm']:.2f} ohm",
        "Shunt resistance, each": f"{assumptions['shunt_nominal_ohm']:.2f} ohm",
        "Main / branch fuse cold R": f"{assumptions['main_fuse_cold_ohm']:.3f} / {assumptions['branch_fuse_cold_ohm']:.3f} ohm",
    }
    for quantity, wanted in table1_expected.items():
        check(f"Table I data: {quantity}", rows1.get(quantity) == wanted,
              {"actual": rows1.get(quantity), "expected": wanted})

    base_trace = csv_rows(root, "simulations/results/hardware-runtime-baseline.csv")
    priority_trace = csv_rows(root, "simulations/results/hardware-runtime-priority.csv")
    for label, rows, endpoint in [("baseline", base_trace, bh), ("priority", priority_trace, ph)]:
        check(f"{label} endpoint matches raw trace", abs(float(rows[-1]["time_s"])/3600-endpoint) < 1e-12)
        check(f"{label} raw endpoint crosses true SOC reserve", float(rows[-1]["true_soc_pct"]) <= assumptions["reserve_pct"])
    first_off = next(row for row in priority_trace if row["state"] == "PRIORITY")
    check("fan shedding time matches raw state transition", abs(float(first_off["time_s"])/3600-fh) < 1e-12)
    sweep = csv_rows(root, "simulations/results/hardware-runtime-sensitivity.csv")
    check("all 18 sensitivity pairs retained", len(sweep) == 18)
    check("priority supplies longer lamp service in each reported pair",
          all(float(row["priority_h"]) > float(row["baseline_h"]) for row in sweep))
    contains("C025", [f"{ph-bh:.4f} h", f"{bh-fh:.4f} h", f"+{gain:.2f}%", f"-{loss:.2f}%"], "C025 service changes")
    heuristic = assumptions["capacity_ah"] * 12.8 * (float(first_off["estimated_soc_pct"])-assumptions["reserve_pct"]) / 100 / float(first_off["load_sensor_w"])
    remaining = bh-fh
    contains("C027", [f"{heuristic:.4f} h", f"{remaining:.4f} h", f"{(heuristic-remaining)*3600:.0f} s"], "C027 heuristic counterfactual")
    dc = next(row for row in hw["dc_cases"] if row["case"] == "starter_2_5W_each")
    for key in ["output_a", "battery_a", "rail_v", "lamp_v", "fan_v", "converter_loss_w", "output_path_loss_w", "two_shunts_loss_w"]:
        contains("C028", [f"{dc[key]:.4f}"], f"C028 DC result {key}")
    for key in ["baseline_h", "priority_h"]:
        values = [float(row[key]) for row in sweep]
        contains("C029", [f"{min(values):.4f}-{max(values):.4f} h"], f"C029 range of {key}")
    error = read_json(root, "simulations/results/system-summary.json")["capacity_and_offset_error"]
    pp_error = 100*error["hours"]*(error["true_discharge_A"]/error["true_capacity_Ah"]-error["measured_discharge_A"]/error["configured_capacity_Ah"])
    contains("C029", [f"{pp_error:.1f} percentage-point"], "C029 SOC error recomputed")
    startup = hw["startup_cases"]
    check("six startup cases retained", len(startup) == 6)
    check("three startup cases fail the stated rail screen", sum(row["min_rail_v"] < assumptions["rail_screening_floor_v"] for row in startup) == 3 and "Three startup cases fail" in m["abstract"])
    for index, key, cid, decimals in [(2,"min_rail_v","C030",3), (4,"min_rail_v","C030",3), (5,"min_rail_v","C031",4), (5,"min_fan_terminal_v","C031",4)]:
        contains(cid, [f"{startup[index][key]:.{decimals}f} V"], f"{cid} S{index+1} {key}")
    for index, result in enumerate(hw["convergence_checks"]):
        contains("C034", [f"{result['runtime_difference_s']:.2f}"], f"C034 convergence {index+1}")
    spice = read_json(root, "simulations/results/spice-summary.json")
    for resistance in [2200,4700]:
        row = next(row for row in spice["cases"] if row["case"] == f"I2C rise with {resistance} ohm at 400 pF")
        contains("C032", [f"{row['rise_30_70_ns']:.0f} ns"], f"C032 rise time {resistance} ohm")
    shunt = assumptions["shunt_nominal_ohm"]
    contains("C032", [f"{2**2*shunt:.1f} W", f"{2*2*shunt:.1f} V", f"{2*2**2*shunt:.1f} W"], "C032 shunt arithmetic")
    caption3 = next(figure["caption"] for figure in figures["figures"] if figure["figure_id"] == "fig3_runtime")
    check("Figure 3 caption reports paired outcomes", all(value in caption3 for value in [f"{bh:.3f}", f"{ph:.3f}", f"{fh:.3f}", f"{gain:.2f}%", f"{loss:.2f}%"]))
    check("Conclusion reports computed service tradeoff", f"{gain:.2f}%" in prose["C039"] and f"{loss:.2f}%" in prose["C039"])
    return {
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS_MANUSCRIPT_DATA_COMPARISONS" if all(row["pass"] for row in checks) else "FAIL",
        "checks": checks, "passed": sum(row["pass"] for row in checks), "total": len(checks),
        "inputs_sha256": {path: file_sha(root/path) for path in EVIDENCE_PATHS},
        "manuscript_fixture": manuscript is not None,
        "pdf_pages": len(pdf.pages),
        "scope": "Actual canonical abstract, prose, tables and one numeric figure caption checked against saved data; all abstract/prose paragraphs compared with extracted current PDF text. Not a full semantic proof, manual visual review, source verification, physical validation or publication approval.",
        "limitations": ["Numeric prose checks locate expected rounded values in the named paragraph; they do not interpret every sentence or every possible reordered relationship.", "PDF extraction normalizes markup, case and punctuation; it cannot detect visual clipping or corrupt outlined figure glyphs.", "The data are deterministic model outputs; matching them does not validate real hardware."],
    }


def self_test(root=ROOT):
    original = read_json(root, "paper/src/manuscript.json")
    source_before = file_sha(root/"paper/src/manuscript.json")
    altered = copy.deepcopy(original)
    table = next(block for block in altered["blocks"] if block["type"] == "table" and block["number"] == "II")
    table["rows"][0][1] = "999.0000"
    result = audit(root, altered)
    table_rejected = any(row["check"] == "Table II data: Lamp service (h)" and not row["pass"] for row in result["checks"])
    altered = copy.deepcopy(original)
    altered["abstract"] = altered["abstract"].replace("43.96%", "99.99%")
    result = audit(root, altered)
    abstract_rejected = any(row["check"] == "abstract discloses calculated lamp gain and fan loss" and not row["pass"] for row in result["checks"])
    altered = copy.deepcopy(original)
    next(block for block in altered["blocks"] if block.get("id") == "C028")["text"] += " This deliberately inserted prose is absent from the PDF."
    result = audit(root, altered)
    stale_prose_rejected = any(row["check"] == "PDF contains canonical paragraph C028" and not row["pass"] for row in result["checks"])
    unchanged = file_sha(root/"paper/src/manuscript.json") == source_before
    outcome = {"table_value_mutation_rejected": table_rejected, "abstract_percentage_mutation_rejected": abstract_rejected, "stale_PDF_prose_rejected": stale_prose_rejected, "live_source_unchanged": unchanged}
    return {"status": "PASS" if all(outcome.values()) else "FAIL", "checks": outcome}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run in-memory negative fixtures; do not write production evidence")
    args = parser.parse_args()
    try:
        result = self_test() if args.self_test else audit()
    except Exception as error:
        result = {"status": "FAIL", "error": f"{type(error).__name__}: {error}"}
    if not args.self_test:
        (ROOT/"paper/evidence/manuscript-data-audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    compact = {key: result[key] for key in ["status", "passed", "total", "error"] if key in result}
    if args.self_test:
        compact = result
    elif "checks" in result:
        compact["failed"] = [row["check"] for row in result["checks"] if not row["pass"]]
    print(json.dumps(compact, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
