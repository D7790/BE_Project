"""Package a checked draft. This command never creates a visual-review approval."""
from pathlib import Path
import hashlib, json, zipfile, subprocess, sys
from artifact_integrity import build_errors, review_errors
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'paper';E=P/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf=ROOT/'output/pdf/wattsense_research_paper.pdf'
subprocess.run([sys.executable,str(P/'src/check_paper.py')],check=True)
record=json.loads((E/'build-record.json').read_text())
review=json.loads((E/'visual-review.json').read_text(encoding='utf-8'))
errors=build_errors(ROOT,record)+review_errors(ROOT,record,review)
audit=json.loads((E/'final-paper-audit.json').read_text(encoding='utf-8'))
if audit.get('status')!='PASS_DRAFT_PACKAGE_CHECKS' or audit.get('pdf_sha256')!=sha(pdf) or audit.get('manuscript_sha256')!=sha(P/'src/manuscript.json'):
    errors.append('Run current draft-package checks before packaging')
if errors:raise SystemExit('\n'.join(errors))
files=[pdf,ROOT/'output/docx/wattsense_research_paper.docx']
# Include the current audit findings, without duplicating old snapshots or CAD.
auditroot=ROOT/'docs/evidence/recheck-2026-09-30'
for relative in ['hardware/FINDINGS.md','hardware/verification.json','hardware/erc.json','hardware/drc.json','hardware/all-rules-erc.json','hardware/all-rules-drc.json','software/FINDINGS.txt','software/software-audit.json','software/independent-check.json','software/policy-differential.json','paper/paper-review-resolutions.json']:
    files.append(auditroot/relative)
files.append(ROOT/'docs/RECHECK_2026-09-30.md')
files.extend(ROOT/p['render_path'] for p in review['pages'])
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
