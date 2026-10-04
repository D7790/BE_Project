"""Create the editable Word companion from the canonical manuscript.

Run with the Codex bundled Python, which supplies python-docx/lxml.
The Word companion intentionally uses a simple single-column editing layout.
The separate PDF is the two-column IEEE-style presentation version.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import sys
from datetime import datetime, timezone
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
OUT = ROOT / "output/docx/wattsense_research_paper.docx"
RECORD = PAPER / "evidence/docx-build-record.json"
SOURCE = PAPER / "src/manuscript.json"
FIGURES = PAPER / "figures/figure-provenance.json"
MNS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def element(name, text=None, **attrs):
    e = OxmlElement(name)
    for k, value in attrs.items():
        e.set(qn(k), str(value))
    if text is not None:
        e.text = text
    return e


def math_run(text):
    r = element("m:r")
    props = element("w:rPr")
    props.append(element("w:rFonts", **{"w:ascii": "Cambria Math", "w:hAnsi": "Cambria Math"}))
    props.append(element("w:sz", **{"w:val": 22}))
    r.append(props)
    t = element("m:t", text)
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r


def sub(base, suffix):
    s = element("m:sSub")
    a = element("m:e"); a.append(math_run(base))
    b = element("m:sub"); b.append(math_run(suffix))
    s.extend([a, b])
    return s


def sup(base, suffix):
    s = element("m:sSup")
    a = element("m:e"); a.append(math_run(base))
    b = element("m:sup"); b.append(math_run(suffix))
    s.extend([a, b])
    return s


def frac(numerator, denominator):
    f = element("m:f")
    n = element("m:num"); n.extend(numerator)
    d = element("m:den"); d.extend(denominator)
    f.extend([n, d])
    return f


def sqrt(children):
    r = element("m:rad")
    props = element("m:radPr"); props.append(element("m:degHide", **{"m:val": 1}))
    r.append(props)
    r.append(element("m:deg"))
    e = element("m:e"); e.extend(children); r.append(e)
    return r


def equation_children(number):
    # OMML carries real mathematical structure; no equation is an image.
    if number == 1:
        return [math_run("s[k+1] = clip(s[k] − "), frac([math_run("100 "), sub("I", "eff"), math_run(" dt")], [math_run("3600 C")]), math_run(", 0, 100).")]
    if number == 2:
        return [sub("E", "est"), math_run(" = "), frac([math_run("C "), sub("V", "nom"), math_run(" max(s − "), sub("s", "res"), math_run(", 0)")], [math_run("100")]), math_run(",")]
    if number == 3:
        return [sub("T", "est"), math_run(" = "), frac([sub("E", "est")], [sub("P", "U2")]), math_run(",     "), sub("P", "U2"), math_run(" > 0.2 W.")]
    if number == 4:
        return [math_run("I = "), frac([math_run("2P")], [math_run("V + "), sqrt([sup("V", "2"), math_run(" − 4RP")])]), math_run(".")]
    raise ValueError(number)


def add_equation(doc, block):
    p = doc.add_paragraph(style="Equation")
    om = element("m:oMath")
    om.extend(equation_children(block["number"]))
    p._p.append(om)
    p.add_run(f"     ({block['number']})")


def rich_text(p, text, bold=False):
    """Preserve prose exactly, apart from rendering explicit markup as native runs."""
    parts = re.split(r"(<sub>.*?</sub>|<super>.*?</super>)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("<sub>"):
            run = p.add_run(html.unescape(part[5:-6])); run.font.subscript = True
        elif part.startswith("<super>"):
            run = p.add_run(html.unescape(part[7:-8])); run.font.superscript = True
        else:
            run = p.add_run(html.unescape(part))
        run.bold = bold


def hyperlink(paragraph, label, url):
    rel = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = element("w:hyperlink")
    link.set(qn("r:id"), rel)
    r = element("w:r"); rp = element("w:rPr")
    rp.append(element("w:color", **{"w:val": "1C4D72"}))
    rp.append(element("w:u", **{"w:val": "single"}))
    r.append(rp); r.append(element("w:t", label)); link.append(r); paragraph._p.append(link)


def configure(doc):
    sec = doc.sections[0]
    sec.page_width = Inches(8.5); sec.page_height = Inches(11)
    sec.top_margin = Inches(.7); sec.bottom_margin = Inches(.7)
    sec.left_margin = Inches(.75); sec.right_margin = Inches(.75)
    sec.header_distance = Inches(.3); sec.footer_distance = Inches(.3)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"; normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.05
    normal.paragraph_format.widow_control = True
    for name in ["Title", "Subtitle", "Heading 1", "Heading 2", "Caption"]:
        s = doc.styles[name]; s.font.name = "Times New Roman"; s.font.color.rgb = RGBColor(0, 0, 0)
    title = doc.styles["Title"]
    title.font.size = Pt(20); title.font.bold = False
    title.paragraph_format.space_after = Pt(12)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name, size, ital in [("Heading 1", 11.5, False), ("Heading 2", 11, True)]:
        s = doc.styles[name]; s.font.size = Pt(size); s.font.italic = ital; s.font.bold = not ital
        s.paragraph_format.space_before = Pt(10); s.paragraph_format.space_after = Pt(5)
        s.paragraph_format.keep_with_next = True
    cap = doc.styles["Caption"]
    cap.font.size = Pt(9); cap.font.italic = False
    cap.paragraph_format.space_before = Pt(3); cap.paragraph_format.space_after = Pt(9)
    for name in ["Equation", "References", "Table Text"]:
        if name not in doc.styles:
            doc.styles.add_style(name, 1)
        s = doc.styles[name]; s.base_style = normal
    eq = doc.styles["Equation"]
    eq.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    eq.paragraph_format.space_before = Pt(4); eq.paragraph_format.space_after = Pt(8)
    eq.paragraph_format.keep_together = True
    ref = doc.styles["References"]
    ref.font.size = Pt(10)
    ref.paragraph_format.left_indent = Inches(.26); ref.paragraph_format.first_line_indent = Inches(-.26)
    ref.paragraph_format.keep_together = True
    table = doc.styles["Table Text"]
    table.font.size = Pt(10); table.paragraph_format.space_after = Pt(0)
    table.paragraph_format.line_spacing = 1.0
    foot = sec.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = foot.add_run(); run.font.name = "Times New Roman"; run.font.size = Pt(9)
    fld = element("w:fldSimple", **{"w:instr": "PAGE"})
    rr = element("w:r"); rr.append(element("w:t", "1")); fld.append(rr); foot._p.append(fld)
    # Do not ask Word to update equation numbers or reformat citations on opening.
    compat = doc.settings.element.find(qn("w:compat"))
    if compat is None:
        compat = element("w:compat"); doc.settings.element.append(compat)
    # Word 2013+ layout behavior.
    compat.append(element("w:compatSetting", **{"w:name": "compatibilityMode", "w:uri": "http://schemas.microsoft.com/office/word", "w:val": "15"}))


def add_table(doc, block):
    p = doc.add_paragraph(style="Caption")
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"TABLE {block['number']}  {block['title']}").bold = True
    t = doc.add_table(rows=1, cols=len(block["headers"]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    widths = [7 * x for x in block["widths"]]
    for col, width in zip(t.columns, widths):
        col.width = Inches(width)
    props = t._tbl.tblPr
    borders = element("w:tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        borders.append(element("w:" + side, **{"w:val": "single", "w:sz": 4, "w:color": "D9D9D9"}))
    props.append(borders)
    margins = element("w:tblCellMar")
    for side in ["top", "bottom", "left", "right"]:
        margins.append(element("w:" + side, **{"w:w": 85, "w:type": "dxa"}))
    props.append(margins)
    rows = [block["headers"]] + block["rows"]
    for i, values in enumerate(rows):
        row = t.rows[0] if i == 0 else t.add_row()
        row._tr.get_or_add_trPr().append(element("w:cantSplit"))
        if i == 0:
            row._tr.get_or_add_trPr().append(element("w:tblHeader"))
        for j, (cell, val) in enumerate(zip(row.cells, values)):
            cell.width = Inches(widths[j]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]; p.style = doc.styles["Table Text"]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = i < len(rows) - 1
            p.add_run(str(val)).bold = i == 0
            if i == 0:
                cell._tc.get_or_add_tcPr().append(element("w:shd", **{"w:fill": "E8EDF2"}))
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def build():
    m = json.loads(SOURCE.read_text(encoding="utf-8"))
    fp = json.loads(FIGURES.read_text(encoding="utf-8"))
    figs = {f["figure_id"].split("_", 1)[1]: f for f in fp["figures"]}
    doc = Document(); configure(doc)
    doc.core_properties.title = m["title"]
    doc.core_properties.author = ", ".join(m["authors"])
    doc.core_properties.subject = "Editable companion to the Wattsense design and simulation manuscript"
    doc.core_properties.comments = "Text, tables and native Office Math equations are editable. Original figures are embedded images; their editable SVG sources and plotting code accompany the project."
    doc.add_paragraph(m["title"], style="Title")
    p = doc.add_paragraph(", ".join(m["authors"])); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    p = doc.add_paragraph(m["status"]); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs: r.font.size = Pt(9); r.italic = True
    if m.get("affiliation"):
        doc.add_paragraph(m["affiliation"])
    doc.add_paragraph("Abstract", style="Heading 1")
    doc.add_paragraph(m["abstract"])
    p = doc.add_paragraph(); p.add_run("Index Terms — ").bold = True; p.add_run(m["keywords"]).italic = True
    inputs = [SOURCE, FIGURES, Path(__file__).resolve()]
    for b in m["blocks"]:
        kind = b["type"]
        if kind in ("h1", "h2"):
            doc.add_paragraph(b["text"], style="Heading 1" if kind == "h1" else "Heading 2")
        elif kind == "p":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich_text(p, b["text"])
        elif kind == "equation":
            add_equation(doc, b)
        elif kind == "table":
            add_table(doc, b)
        elif kind == "figure":
            f = figs[b["figure"]]
            path = ROOT / next(x for x in f["files"] if x.endswith(".png")); inputs.append(path)
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True; p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(1)
            # Diagrams retain full source size. Charts grow moderately for easy editing.
            width = 7 if b["number"] <= 2 else 4.9
            pic = p.add_run().add_picture(str(path), width=Inches(width))
            pic._inline.docPr.set("descr", f["alt_text"])
            pic._inline.docPr.set("title", f"Figure {b['number']}")
            p = doc.add_paragraph(f"Fig. {b['number']}. {f['caption']}", style="Caption")
            p.paragraph_format.keep_together = True
        else:
            raise ValueError(kind)
    doc.add_paragraph("References", style="Heading 1")
    for r in m["references"]:
        p = doc.add_paragraph(style="References")
        p.add_run(f"[{r['number']}] {r['text']} ")
        hyperlink(p, "Source", r["url"])
    OUT.parent.mkdir(parents=True, exist_ok=True); doc.save(OUT)
    audit = check_content(m, fp)
    record = {
        "status": "CONTENT_VALIDATED_VISUAL_QA_PENDING",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": sys.executable,
        "output": OUT.relative_to(ROOT).as_posix(),
        "docx_sha256": sha(OUT),
        "inputs_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        "layout": "US Letter, single column, 0.75 inch horizontal margins, Times New Roman 11 pt; editable companion to the two-column PDF",
        "editable": {"body": True, "tables": True, "equations": "4 native OMML equations", "figures": "5 embedded original 300 dpi PNGs; editable SVG and plotting sources are in paper/figures and paper/src/make_figures.py"},
        "content_validation": audit,
        "visual_qa": {"status": "PENDING", "pages_inspected": [], "reason": None},
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


def check_content(m=None, fp=None):
    m = m or json.loads(SOURCE.read_text(encoding="utf-8"))
    fp = fp or json.loads(FIGURES.read_text(encoding="utf-8"))
    doc = Document(OUT)
    paras = [p.text for p in doc.paragraphs]
    checks = []
    def expect(name, passed):
        checks.append({"check": name, "pass": bool(passed)})
    for name in ["title", "abstract", "status"]:
        expect(name + " preserved exactly", m[name] in paras)
    expect("author order preserved", ", ".join(m["authors"]) in paras)
    for b in m["blocks"]:
        if b["type"] == "p":
            expect(b["id"] + " prose preserved exactly", html.unescape(b["text"]) in paras)
        elif b["type"] in ["h1", "h2"]:
            expect(b["text"] + " heading preserved", b["text"] in paras)
    source_tables = [b for b in m["blocks"] if b["type"] == "table"]
    expect("two editable tables", len(doc.tables) == 2)
    for source, target in zip(source_tables, doc.tables):
        expect("table " + source["number"] + " all cells preserved", [[c.text for c in row.cells] for row in target.rows] == [source["headers"]] + source["rows"])
    for i, f in enumerate(fp["figures"], 1):
        expect(f"figure {i} caption preserved", f"Fig. {i}. {f['caption']}" in paras)
    for r in m["references"]:
        expect(f"reference {r['number']} preserved", any(p.startswith(f"[{r['number']}] {r['text']}") for p in paras))
    with ZipFile(OUT) as z:
        root = etree.fromstring(z.read("word/document.xml"))
        ns = {"m": MNS, "w": WNS, "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
        math = root.findall(".//m:oMath", ns)
        expect("four native Office Math equations", len(math) == 4)
        expected = ["s[k+1] = clip(s[k] − 100 Ieff dt3600 C, 0, 100).", "Eest = C Vnom max(s − sres, 0)100,", "Test = EestPU2,     PU2 > 0.2 W.", "I = 2PV + V2 − 4RP."]
        for number, (node, wanted) in enumerate(zip(math, expected), 1):
            text = "".join(node.xpath(".//m:t/text()", namespaces=ns))
            expect(f"equation {number} symbols retained", text == wanted)
        expect("four structured fractions", len(root.findall(".//m:f", ns)) == 4)
        expect("one structured square root", len(root.findall(".//m:rad", ns)) == 1)
        expect("five embedded original figures", len(root.findall(".//wp:inline", ns)) == 5)
        expect("all figures have alt text", all(n.get("descr") for n in root.findall(".//wp:docPr", ns)))
        rel = etree.fromstring(z.read("word/_rels/document.xml.rels"))
        targets = {x.get("Target") for x in rel if x.get("Type", "").endswith("/hyperlink")}
        expect("nine live source links", targets == {r["url"] for r in m["references"]})
        expect("editable file has no protection", b"documentProtection" not in z.read("word/settings.xml"))
        expect("ZIP integrity", z.testzip() is None)
    result = {"passed": sum(c["pass"] for c in checks), "total": len(checks), "checks": checks}
    if result["passed"] != result["total"]:
        raise AssertionError(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(check_content(), indent=2))
    else:
        build()
