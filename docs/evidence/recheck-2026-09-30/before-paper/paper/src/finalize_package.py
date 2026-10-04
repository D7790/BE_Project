"""Save the completed assistant visual review and an explicitly scoped review ZIP."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'paper';E=P/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf=ROOT/'output/pdf/wattsense_research_paper.pdf'
record=json.loads((E/'build-record.json').read_text())
assert record['pdf_sha256']==sha(pdf)
record.update(status='PASS_ASSISTANT_VISUAL_QA',visual_review=dict(reviewer='Codex assistant',date='2026-09-30',pages=list(range(1,8)),method='Poppler PNG rendering at 110 dpi and visual inspection of every final page; figure SVG and PNG QA separately recorded',findings='No clipping, content overlap, missing glyphs, orphan section heading or unresolved figure/table placement defect observed. This is assistant QA, not human author approval.'),manuscript_sha256=sha(P/'src/manuscript.json'))
(E/'build-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
files=[pdf]
for f in P.rglob('*'):
    if not f.is_file() or f.suffix in ['.zip','.pyc'] or '__pycache__' in f.parts:continue
    if 'originality-corpus' in f.parts and not f.name.endswith(('.provenance.json','.excerpt.json')):continue
    if f.name=='review-package-manifest.json':continue
    files.append(f)
files=sorted(set(files))
manifest=dict(scope='Paper review package, not a standalone full project runtime. See paper/READ_ME_FIRST.md. Full reference corpus PDF/text excluded; original inputs remain local.',hardware_results=False,submission_ready=False,files=[dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f)) for f in files])
mp=E/'review-package-manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');files.append(mp)
archive=P/'wattsense-paper-review.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for f in files:z.write(f,f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for f in manifest['files']:
        assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
print(json.dumps(dict(archive=str(archive),entries=len(files),size_bytes=archive.stat().st_size,sha256=sha(archive),crc='PASS',entry_hashes='PASS',pdf_sha256=sha(pdf)),indent=2))
