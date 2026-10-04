"""Hash-bound build and visual-review checks; no function grants human approval."""
from pathlib import Path
import hashlib
import json


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def input_paths(root):
    paths = ["paper/src/manuscript.json", "paper/src/build_paper.py",
             "paper/src/artifact_integrity.py", "paper/requirements-paper.txt",
             "paper/figures/figure-provenance.json"]
    for fig in read(root / "paper/figures/figure-provenance.json")["figures"]:
        paths.extend(p for p in fig["files"] if p.endswith(".svg"))
    return sorted(set(paths))


OUTPUTS = ["output/pdf/wattsense_research_paper.pdf", "paper/wattsense-manuscript.md",
           "paper/evidence/manuscript-with-evidence.md", "paper/evidence/rendered-manuscript.txt"]


def hashes(root, paths):
    return {p: sha(root / p) for p in paths}


def build_errors(root, record):
    """Reject missing bindings as well as modified artifacts; never refresh hashes here."""
    errors = []
    for label, expected in [("inputs", input_paths(root)), ("outputs", OUTPUTS)]:
        stored = record.get(label + "_sha256", {})
        if set(stored) != set(expected):
            errors.append(f"Build {label} inventory does not match required files")
        for path in expected:
            if not (root / path).is_file() or stored.get(path) != sha(root / path):
                errors.append(f"Changed or unbound build {label}: {path}")
    if record.get("pdf_sha256") != sha(root / OUTPUTS[0]):
        errors.append("Build record PDF hash differs from current PDF")
    if record.get("manuscript_sha256") != sha(root / "paper/src/manuscript.json"):
        errors.append("Build record manuscript hash differs from current manuscript")
    return errors


def review_errors(root, record, review):
    errors = []
    if review.get("status") != "PASS_ASSISTANT_VISUAL_QA":
        errors.append("Visual review has not passed")
    if review.get("pdf_sha256") != record.get("pdf_sha256"):
        errors.append("Visual review is for a different PDF")
    if review.get("human_review_complete") is not False:
        errors.append("Assistant visual QA must not grant human approval")
    if not review.get("reviewer") or not review.get("reviewed_at") or not review.get("findings"):
        errors.append("Visual review requires reviewer, time and findings")
    pages = review.get("pages", [])
    if [p.get("page") for p in pages] != list(range(1, record["pages"] + 1)):
        errors.append("Visual review must cover every page once in order")
    for page in pages:
        rel = Path(page.get("render_path", ""))
        target = (root / rel).resolve()
        if rel.is_absolute() or not target.is_relative_to(root.resolve()):
            errors.append("Visual review render path escapes project")
        elif not target.is_file() or page.get("sha256") != sha(target):
            errors.append(f"Missing or changed page render: {rel}")
    return errors
