"""Adversarial regression checks for stale-build and unsupported-QA acceptance."""
from pathlib import Path
import json
import tempfile
import unittest
from artifact_integrity import OUTPUTS, build_errors, hashes, input_paths, review_errors, sha


class ArtifactIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("paper/figures/figure-provenance.json", json.dumps({"figures": [{"files": ["paper/figures/one.svg"]}]}))
        for name in input_paths(self.root) + OUTPUTS:
            if not (self.root / name).exists(): self.write(name, "fixture")
        self.record = {"inputs_sha256": hashes(self.root, input_paths(self.root)),
                       "outputs_sha256": hashes(self.root, OUTPUTS), "pages": 1,
                       "pdf_sha256": sha(self.root / OUTPUTS[0]),
                       "manuscript_sha256": sha(self.root / "paper/src/manuscript.json")}
        self.write("tmp/render/page-1.png", "render fixture")
        self.review = {"status": "PASS_ASSISTANT_VISUAL_QA", "pdf_sha256": self.record["pdf_sha256"],
                       "reviewer": "test fixture", "reviewed_at": "2026-09-30T00:00:00+00:00",
                       "findings": "fixture only", "human_review_complete": False,
                       "pages": [{"page": 1, "render_path": "tmp/render/page-1.png",
                                  "sha256": sha(self.root / "tmp/render/page-1.png")}]}

    def write(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value, encoding="utf-8")

    def test_current_binding_accepted(self):
        self.assertEqual(build_errors(self.root, self.record), [])
        self.assertEqual(review_errors(self.root, self.record, self.review), [])

    def test_changed_manuscript_rejected(self):
        self.write("paper/src/manuscript.json", "changed")
        self.assertTrue(build_errors(self.root, self.record))

    def test_changed_figure_rejected(self):
        self.write("paper/figures/one.svg", "changed")
        self.assertTrue(build_errors(self.root, self.record))

    def test_changed_pdf_rejected(self):
        self.write(OUTPUTS[0], "changed")
        self.assertTrue(build_errors(self.root, self.record))

    def test_missing_input_binding_rejected(self):
        self.record["inputs_sha256"].pop("paper/src/build_paper.py")
        self.assertTrue(build_errors(self.root, self.record))

    def test_visual_review_wrong_pdf_rejected(self):
        self.review["pdf_sha256"] = "obsolete"
        self.assertTrue(review_errors(self.root, self.record, self.review))

    def test_missing_reviewed_page_rejected(self):
        self.review["pages"] = []
        self.assertTrue(review_errors(self.root, self.record, self.review))

    def test_changed_render_rejected(self):
        self.write("tmp/render/page-1.png", "changed")
        self.assertTrue(review_errors(self.root, self.record, self.review))

    def test_no_automatic_human_approval(self):
        self.review["human_review_complete"] = True
        self.assertTrue(review_errors(self.root, self.record, self.review))


if __name__ == "__main__": unittest.main(verbosity=2)
