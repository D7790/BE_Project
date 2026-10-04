"""Check this local draft package without inventing human approval or network review."""
from pathlib import Path
import collections, csv, hashlib, json, re, subprocess, sys
from pypdf import PdfReader
from artifact_integrity import build_errors, review_errors
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'paper'; E=P/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,condition,detail=None):
    checks.append(dict(check=name,pass_=bool(condition),detail=detail))
m=read(P/'src/manuscript.json'); h=read(ROOT/'simulations/results/hardware-summary.json')
numeric_proc=subprocess.run([sys.executable,str(P/'src/check_manuscript_data.py')],capture_output=True,text=True,encoding='utf-8')
check('actual manuscript prose and tables match data and PDF',numeric_proc.returncode==0,numeric_proc.stdout.strip() or numeric_proc.stderr.strip())
pdf=ROOT/'output/pdf/wattsense_research_paper.pdf';r=PdfReader(pdf)
build=read(E/'build-record.json')
errors=build_errors(ROOT,build)
check('PDF build is bound to current inputs and generated outputs',not errors,errors)
review_path=E/'visual-review.json'
errors=review_errors(ROOT,build,read(review_path)) if review_path.exists() else ['No hash-bound visual-review record']
check('all current PDF pages have recorded visual QA',not errors,errors)
check('build record actual page count',build['pages']==len(r.pages))
check('seven-page manuscript',len(r.pages)==7)
check('four supplied authors in order',m['authors']==['Dhanesh Chaudhari','Ujjwal Kshirsagar','Mrudula Pagar','Yash Ahire'])
check('no invented affiliation',m['affiliation'] is None)
text='\n'.join(p.extract_text() for p in r.pages)
check('every author in PDF',all(n in text for n in m['authors']))
check('all nine references numbered',[x['number'] for x in m['references']]==list(range(1,10)))
check('working draft and simulation scope visible','WORKING DRAFT' in text and 'No physical measurements' in text)
check('no replacement glyph in extracted prose','\ufffd' not in text and '\u25a0' not in text)
links=[]
for page in r.pages:
    for a in page.get('/Annots',[]):
        obj=a.get_object();action=obj.get('/A',{})
        if action.get('/S')=='/URI':links.append(str(action['/URI']))
check('nine linked bibliography sources',len(set(links))==9)
check('abstract runtimes match',all(f'{v:.3f}' in m['abstract'] for v in [h['baseline']['runtime_to_common_endpoint_h'],h['priority']['runtime_to_common_endpoint_h'],h['priority']['fan_service_h']]))
check('both service changes disclosed','43.96%' in m['abstract'] and '-54.47%' in m['abstract'])
check('current suite pass',read(ROOT/'simulations/results/suite-summary.json')['status']=='PASS')
check('45 Python tests recorded','Ran 45 tests' in (ROOT/'simulations/results/python-tests.log').read_text())
cpp=read(ROOT/'simulations/results/firmware-host-summary.json')
check('67 host assertions',sum(x['assertions'] for x in cpp['results'])+cpp['register_reader']['assertions']==67)
check('hardware remains unarmed',cpp['production_hardware_confirmed'] is False)
check('18 scenario pairs and six startup cases',len(h['sensitivity_pairs'])==18 and len(h['startup_cases'])==6)
index=read(E/'local-evidence-index.json')
for eid,files in index.items():check(f'{eid} current local evidence hashes',all(sha(ROOT/x['path'])==x['sha256'] for x in files))
fp=read(P/'figures/figure-provenance.json')
for f in fp['figures']:
    check(f'{f["figure_id"]} source hashes',all(sha(ROOT/x['path'])==x['sha256'] for x in f['source_files']))
    check(f'{f["figure_id"]} output hashes',all(sha(ROOT/x)==f['output_sha256'][Path(x).suffix[1:]] for x in f['files']))
with (E/'claims.csv').open(encoding='utf-8') as stream:claims=list(csv.DictReader(stream))
ids=[c['claim_id'] for c in claims];sids={x['evidence_id'] for x in read(E/'source_manifest.json')['sources']}
check('53 unique claim records',len(ids)==len(set(ids))==53)
check('claim evidence IDs resolve',all(set(c['evidence_ids'].split(';'))<=sids for c in claims))
check('human verification not invented',all(c['verification_status']=='unverified' for c in claims))
o=read(E/'originality-report.json')
check('originality report matches final manuscript',o['manuscript_sha256']==sha(P/'src/manuscript.json'))
fq=read(P/'figures/figure-qa.json')
check('visual figure QA matches current figures',all(fq['files_sha256'].get(Path(x).name)==sha(ROOT/x) for f in fp['figures'] for x in f['files']))
word=read(E/'docx-build-record.json')
check('editable Word matches current manuscript and source figures',all(sha(ROOT/path)==digest for path,digest in word['inputs_sha256'].items()) and sha(ROOT/word['output'])==word['docx_sha256'])
check('Word content validated with visual-render limitation explicit',word['content_validation']['passed']==word['content_validation']['total']==102 and word['status']=='CONTENT_VALIDATED_RENDER_UNVERIFIED')
skill=Path('C:/Users/dhane/.codex/skills/scientific-writing/scripts')
commands=[('consistency','check_consistency.py',[str(E/'consistency_manifest.json')]),('reference-syntax','check_references.py',[str(E/'source_manifest.json')]),('source-schema','validate_manifest.py',[str(E/'source_manifest.json'),'--kind','source']),('draft-lint','lint_manuscript.py',[str(E/'manuscript-with-evidence.md'),'--manifest',str(E/'manuscript_manifest.json')]),('claim-human-gate','audit_claims.py',[str(E/'manuscript-with-evidence.md'),str(E/'claims.csv'),str(E/'source_manifest.json')]),('authorship-human-gate','validate_authorship.py',[str(E/'authorship.json')])]
skillresults=[]
for name,script,args in commands:
    proc=subprocess.run([sys.executable,str(skill/script),*args],capture_output=True,text=True,encoding='utf-8')
    data=json.loads(proc.stdout);(E/f'skill-{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    codes=dict(collections.Counter(x['code'] for x in data.get('issues',[])))
    skillresults.append(dict(check=name,status=data['status'],exit_code=proc.returncode,codes=codes))
    if name in ['consistency','reference-syntax','source-schema']:check(f'skill {name}',proc.returncode==0,codes)
save=dict(status='PASS_DRAFT_PACKAGE_CHECKS' if all(c['pass_'] for c in checks) else 'FAIL',checks=checks,passed=sum(c['pass_'] for c in checks),pdf_sha256=sha(pdf),manuscript_sha256=sha(P/'src/manuscript.json'),skill_results=skillresults,submission_ready=False,physical_measurements=False,human_review_complete=False,interpretation='Internal checks only. Human gates deliberately remain incomplete. Scenario sample_size fields count deterministic cases, not experimental subjects/trials.')
(E/'final-paper-audit.json').write_text(json.dumps(save,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':save['status'],'passed':save['passed'],'total':len(checks),'failures':[c for c in checks if not c['pass_']],'skill_results':skillresults},indent=2))
if save['status']=='FAIL':sys.exit(1)
