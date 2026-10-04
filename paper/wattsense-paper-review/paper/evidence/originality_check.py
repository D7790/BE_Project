"""Bounded local wording overlap audit. The manuscript is never sent over a network.

Run with the bundled Python (pypdf installed). Optional --download retrieves only
fixed public reference URLs; default execution is entirely offline. Reference
copies are local audit inputs, not a corpus licensed for redistribution.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORPUS = HERE / "originality-corpus"
MANUSCRIPT = ROOT / "paper/src/manuscript.json"
SOURCES = [
    {
        "id": "movassagh2021", "format": "pdf", "coverage": "full article plus references",
        "url": "https://ntrs.nasa.gov/api/citations/20220008848/downloads/2021.07%20-%20Energies%20-%20A%20Critical%20Look%20at%20Coulomb%20Counting%20Approach%20for%20State%20of%20Charge%20Estimation.pdf",
        "doi": "10.3390/en14144074",
    },
    {
        "id": "zhang2018", "format": "pdf", "coverage": "full article plus references and repository cover",
        "url": "https://wrap.warwick.ac.uk/id/eprint/94268/9/WRAP-online-estimation-battery-Marco-2017.pdf",
        "alternate_url": "https://pure.coventry.ac.uk/ws/portalfiles/portal/27426271/Binder9.pdf",
        "doi": "10.1016/j.energy.2017.10.043",
    },
    {
        "id": "marahatta2021", "format": "html", "coverage": "author-uploaded article in page text, including page furniture",
        "url": "https://www.researchgate.net/publication/346036129_Priority-based_low_voltage_DC_microgrid_system_for_rural_electrification",
        "doi": "10.1016/j.egyr.2020.11.030",
    },
    {
        "id": "rajbhandari2024", "format": "html", "coverage": "publisher full article in page text, including page furniture",
        "url": "https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/stg2.12151",
        "doi": "10.1049/stg2.12151",
    },
]


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("\u00ad", "")
    # Join line-end hyphenation only; regular compound hyphens become spaces.
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"\[(?:\d+[, -]*)+\]", " ", text)
    return re.findall(r"[a-z0-9]+", text)


def manuscript_sections(doc):
    yield "abstract", doc["abstract"]
    for block in doc["blocks"]:
        if block.get("type") == "p":
            yield block.get("id", "unlabelled"), block["text"]


def prepare_source(source, download):
    CORPUS.mkdir(exist_ok=True)
    raw_path = CORPUS / f"{source['id']}.{source['format']}"
    text_path = CORPUS / f"{source['id']}.txt"
    info = dict(source)
    metadata_path = CORPUS / f"{source['id']}.provenance.json"
    if metadata_path.exists():
        info.update(json.loads(metadata_path.read_text(encoding="utf-8")))
    info["retrieved_date"] = "2026-09-30"
    info["status"] = "unavailable"
    info["raw_path"] = str(raw_path.relative_to(ROOT)).replace("\\", "/")
    if download and not raw_path.exists():
        for url in [source["url"], *([source["alternate_url"]] if source.get("alternate_url") else [])]:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (reference verification; local academic manuscript audit)"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read(12_000_001)
                if len(raw) > 12_000_000:
                    raise ValueError("Reference exceeds the 12 MB local audit limit")
                if source["format"] == "pdf" and not raw.startswith(b"%PDF"):
                    raise ValueError("Response was not a PDF")
                raw_path.write_bytes(raw)
                info["downloaded_from"] = url
                break
            except Exception as exc:
                info.setdefault("retrieval_attempts", []).append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
                info["retrieval_error"] = f"{type(exc).__name__}: {exc}"
    if raw_path.exists():
        raw = raw_path.read_bytes()
        info["raw_sha256"] = sha(raw)
        try:
            if source["format"] == "pdf":
                from pypdf import PdfReader
                reader = PdfReader(raw_path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                info["pages"] = len(reader.pages)
            else:
                parser = VisibleText()
                parser.feed(raw.decode("utf-8", errors="replace"))
                text = "\n".join(parser.parts)
                if len(normalize(text)) < 1500 or source["doi"].casefold() not in text.casefold():
                    raise ValueError("No verified article text; likely access/challenge page")
            text_path.write_text(text, encoding="utf-8")
            info.update(status="available", text_path=str(text_path.relative_to(ROOT)).replace("\\", "/"), text_sha256=sha(text.encode()), normalized_words=len(normalize(text)))
        except Exception as exc:
            info["extraction_error"] = f"{type(exc).__name__}: {exc}"
    # A manually supplied public-source excerpt is allowed only with provenance.
    excerpt_path = CORPUS / f"{source['id']}.excerpt.json"
    if info["status"] != "available" and excerpt_path.exists():
        excerpt = json.loads(excerpt_path.read_text(encoding="utf-8"))
        text = excerpt["text"]
        info.update(status="available", coverage=excerpt["coverage"], excerpt_provenance=excerpt["provenance"], text_sha256=sha(text.encode()), normalized_words=len(normalize(text)))
        text_path.write_text(text, encoding="utf-8")
        info["text_path"] = str(text_path.relative_to(ROOT)).replace("\\", "/")
    metadata_path.write_text(json.dumps(info, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return info


def audit(download=False):
    manuscript_bytes = MANUSCRIPT.read_bytes()
    doc = json.loads(manuscript_bytes)
    corpus = [prepare_source(s, download) for s in SOURCES]
    source_index = {}
    for info in corpus:
        if info["status"] != "available":
            continue
        words = normalize((ROOT / info["text_path"]).read_text(encoding="utf-8"))
        source_index[info["id"]] = {tuple(words[i:i+8]) for i in range(max(0, len(words)-7))}
    overlaps = []
    sections = list(manuscript_sections(doc))
    for claim_id, prose in sections:
        words = normalize(prose)
        for source_id, index in source_index.items():
            matched = [i for i in range(max(0, len(words)-7)) if tuple(words[i:i+8]) in index]
            if not matched:
                continue
            # Merge adjacent matches into the longest continuous local spans.
            spans = []
            for start in matched:
                if spans and start <= spans[-1][1]:
                    spans[-1][1] = max(spans[-1][1], start + 8)
                else:
                    spans.append([start, start + 8])
            for start, end in spans:
                overlaps.append({"claim_id": claim_id, "source_id": source_id, "words": end-start, "normalized_span": " ".join(words[start:end]), "manual_classification": "requires inspection; exact matching alone does not establish plagiarism"})
    report = {
        "audit_date": "2026-09-30",
        "manuscript": "paper/src/manuscript.json",
        "manuscript_sha256": sha(manuscript_bytes),
        "method": "Local case-folded, diacritic-normalized exact eight-word matching, independently within each paragraph; citation brackets, punctuation and source line-end hyphenation normalized. Adjacent windows merged.",
        "draft_scope": "Abstract and prose paragraphs C001-C041; headings, equations, keywords, tables, figure captions and bibliography excluded. No draft text transmitted externally.",
        "paragraphs_checked": len(sections),
        "normalized_draft_words": sum(len(normalize(t)) for _, t in sections),
        "sources_available": len(source_index),
        "source_coverage": corpus,
        "matched_spans": overlaps,
        "claim_citation_review": {
            "C001": "Supported: Marahatta describes charge-threshold priority groups; Rajbhandari describes forecast-assisted allocation. Opening motivation is an explicit physical/design rationale, not an external numerical claim.",
            "C004": "Supported by Movassagh abstract/error taxonomy. The sentence about shared simulator inputs is a project-method inference and is not claimed as that paper's finding.",
            "C005": "Supported by Marahatta section 2.2.2/Table 3 and reported experiment; Rajbhandari sections 2.1-2.2 support forecast/optimization characterization. No external performance metric transferred.",
            "C006": "Supported by Zhang abstract and experimental section 4.1. Need for model characterization is a reasonable explicitly worded inference; remaining sentences refer to the local Wattsense design."
        },
        "manual_wording_review": "The four inspected literature-discussion paragraphs C001/C004/C005/C006 use brief attributed summaries. No distinctive unattributed copying was noticed in that bounded comparison. Terms such as state of charge, coulomb counting and equivalent circuit are standard terminology, not evidence of plagiarism by themselves. This is an assistant review; accountable author/institutional review is pending.",
        "limits": [
            "Not a plagiarism certificate, similarity percentage, or exhaustive originality search.",
            "Coverage is limited to the locally available texts listed; access failures and excerpts are disclosed per source.",
            "Exact eight-word matching misses paraphrase, translation, ideas, shorter copying and extraction/line-break errors; generic technical sequences can produce false positives.",
            "No institutional corpus, paid similarity service, unpublished student theses or proprietary database was searched.",
            "Scientific novelty is separate: priority shedding and coulomb counting are established methods. Author/institutional review remains necessary."
        ],
    }
    out = HERE / "originality-report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    lines = ["WATTSENSE: LIMITED LOCAL ORIGINALITY AND CITATION CHECK", "Audit date: 30 September 2026", "", f"Manuscript SHA-256: {report['manuscript_sha256']}", report["method"], report["draft_scope"], f"Paragraphs checked: {len(sections)}; normalized words: {report['normalized_draft_words']}; available reference texts: {len(source_index)}.", "", "COVERAGE"]
    for item in corpus:
        lines.extend([f"{item['id']}: {item['status']}; {item['coverage']}", item["url"]])
        if item.get("retrieval_error"):
            lines.append(item["retrieval_error"])
        if item.get("extraction_error"):
            lines.append(item["extraction_error"])
    lines.extend(["", "EXACT MATCHES", f"Merged matching spans: {len(overlaps)}."])
    for match in overlaps:
        lines.append(f"{match['claim_id']} / {match['source_id']} / {match['words']} words: {match['normalized_span']}")
    if not overlaps:
        lines.append("No exact eight-word span found within this limited corpus. This is not evidence that no plagiarism exists elsewhere.")
    lines.extend(["", "CITATION REVIEW"])
    lines.extend(f"{key}: {value}" for key, value in report["claim_citation_review"].items())
    lines.extend(["", "MANUAL WORDING REVIEW", report["manual_wording_review"]])
    lines.extend(["", "LIMITATIONS", *report["limits"]])
    (HERE / "originality-report.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps({"sources_available": len(source_index), "merged_matches": len(overlaps), "report": str(out), "source_status": {i["id"]: i["status"] for i in corpus}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download fixed public reference URLs only; no manuscript upload")
    args = parser.parse_args()
    audit(args.download)
