"""Build local manuscript evidence records; never mark human review complete."""
from pathlib import Path
import csv, hashlib, html, json, re, shutil, sys
ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'paper'
E = P / 'evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p, x): p.write_text(json.dumps(x, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m = read(P/'src/manuscript.json')
# One-time citation order normalization, preserving evidence IDs.
if not m.get('citation_order_normalized'):
    mapping={1:3,2:1,3:4,4:2,5:9,6:5,7:6,8:7,9:8}
    def renum(x):
        if isinstance(x,str): return re.sub(r'\[([1-9])\]',lambda a:f'[{mapping[int(a[1])]}]',x)
        if isinstance(x,list): return [renum(v) for v in x]
        if isinstance(x,dict): return {k:renum(v) for k,v in x.items()}
        return x
    m=renum(m); m['citation_order_normalized']=True
for b in m['blocks']:
    if b.get('id')=='C009': b['evidence']=['E101','E007','E008']
    if b.get('id')=='C019': b['text']=b['text'].replace('A negative discriminant','A non-positive discriminant')
    if b.get('id')=='C013': b['text']=b['text'].replace('The deployed configuration','The reference firmware configuration')
    if b.get('id')=='C014': b['text']=b['text'].replace('Firmware samples nominally at 10 Hz and emits telemetry at 1 Hz.','Electrical acquisition and control run nominally at 10 Hz; temperature readings and telemetry refresh at 1 Hz.')
    if b.get('id')=='C033': b['text']=b['text'].replace('The independent publication recheck passes 38 checks.','The independent publication recheck passed 38 checks before separately logged documentation wording corrections.')
lit=read(E/'literature-review.json')
by={x['id']:x for x in lit['sources']}
refs=[
('E002',lit['suggested_bibliography'][1],by['marahatta2021']['url']),
('E004',lit['suggested_bibliography'][2],by['rajbhandari2024']['url']),
('E001',lit['suggested_bibliography'][0],by['movassagh2021']['url']),
('E003',lit['suggested_bibliography'][3],by['zhang2018']['url']),
('E006','Texas Instruments, INA219 Zero-Drift, Bidirectional Current/Power Monitor With I2C Interface, SBOS448G, rev. G, Dec. 2015.','https://www.ti.com/lit/ds/symlink/ina219.pdf'),
('E007','Alpha and Omega Semiconductor, AO3400A: 30 V N-Channel MOSFET, rev. 3.1, July 2023.','https://www.aosmd.com/res/data_sheets/AO3400A.pdf'),
('E008','Littelfuse, 1206 Fast-Acting Fuse: 466 Series, data sheet, accessed Sep. 30, 2026.','https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f'),
('E009','R. Arora, I2C Bus Pull-Up Resistor Calculation, Texas Instruments, SLVA689, Feb. 2015.','https://www.ti.com/lit/an/slva689/slva689.pdf'),
('E005','T. Kassis, V. Agarwal, Y. He, D. Patel, and A. M. Brueckner, Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents, arXiv:2609.00065, 2026, doi: 10.48550/arXiv.2609.00065.','https://arxiv.org/abs/2609.00065')]
m['references']=[dict(number=i+1,evidence_id=e,text=t,url=u) for i,(e,t,u) in enumerate(refs)]
save(P/'src/manuscript.json',m)
sources=[]
def source(e,title,author,year,url,locator,doi='',typ='other',conf='public'):
    sources.append(dict(evidence_id=e,title=title,authors=author,year=year,source_type=typ,confidentiality=conf,
        identifiers=dict(doi=doi,url=url,isbn='',pmcid='',pmid=''),locator=locator,
        verification=dict(status='unverified',source_opened=True,verified_by='',verified_on='')))
for e,key in [('E001','movassagh2021'),('E002','marahatta2021'),('E003','zhang2018'),('E004','rajbhandari2024')]:
    x=by[key]; source(e,x['title'],x['authors'],x['year'],x['url'],x['inspection']+' Accountable human verification pending.',x['doi'], 'journal_article')
for e,t,u in refs[4:]:
    source(e,t,[],2026 if e=='E005' else None,u,'Agent opened primary document 2026-09-30. Human verification pending. '+({'E006':'pp. 1, 3 and 5; description, pin functions and measurement scales.','E007':'pp. 1-2, RDS(on) at VGS=2.5 V and 25 C.','E008':'p. 1 electrical characteristics, nominal cold resistances for 1 A/2 A.','E009':'pp. 1-3, RC rise-time derivation; equations 5-7.','E005':'arXiv metadata, latest v2 inspected; bibliographic attribution of skill.'}[e]))
local={
 'E101':('Hardware design and reference wiring',['hardware/REFERENCE_WIRING.md','hardware/PCB_REQUIREMENTS.md','hardware/pcb/wattsense-main-revB-4layer/wattsense-main.kicad_pcb']),
 'E102':('Implemented controller and acquisition',['firmware/include/controller.h','firmware/include/config.h','firmware/src/main.cpp','wattsense/model.py']),
 'E103':('Nonideal model, assumptions and numerical results',['simulations/hardware-assumptions.json','simulations/hardware_model.py','simulations/run_hardware.py','simulations/results/hardware-summary.json','simulations/results/hardware-runtime-baseline.csv','simulations/results/hardware-runtime-priority.csv','simulations/results/system-summary.json']),
 'E104':('Fresh reproducible software and simulation suite',['simulations/results/suite-summary.json','simulations/results/python-tests.log','simulations/results/firmware-host-summary.json','simulations/run_all.py']),
 'E105':('Reduced circuit simulations',['simulations/run_spice.py','simulations/results/spice-summary.json','simulations/run_hardware.py']),
 'E106':('Native CAD and fabrication audit',['paper/evidence/recheck/publication-evidence-check.json','paper/evidence/recheck/erc.json','paper/evidence/recheck/drc.json','paper/evidence/recheck/ignored-cad-checks.csv']),
 'E109':('Independent numerical/publication recheck',['paper/evidence/recheck/verify_evidence.py','paper/evidence/recheck/publication-evidence-check.json','paper/evidence/methodology-review.txt','paper/evidence/recheck/documentation-finalization.json']),
 'E110':('Planned laboratory validation and local package',['docs/TEST_PLAN.md','docs/LAB_START_GUIDE.md','paper/src/manuscript.json']),
 'E111':('Skill and tool provenance',['paper/evidence/skill-provenance.json'])}
skill=Path('C:/Users/dhane/.codex/skills/scientific-writing/SKILL.md')
save(E/'skill-provenance.json',dict(name='scientific-writing',version='2.1',installed_path=str(skill),sha256=sha(skill),source='https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/scientific-writing',discovery='https://skills.sh/k-dense-ai/scientific-agent-skills/scientific-writing',observed_date='2026-09-30',discovery_installs='2.1K',github_stars_display='47.2K',used_for='evidence mapping, numeric consistency, draft disclosure and review',human_approval_pending=True,browser='Supported hidden in-app browser fallback after isolated shell headless launch was blocked; no literal headless Chrome run claimed.'))
index={}
for e,(title,paths) in local.items():
    index[e]=[dict(path=x,sha256=sha(ROOT/x)) for x in paths]
    source(e,title,[],2026,'','Unpublished local project files: '+', '.join(paths)+'. See local-evidence-index.json for hashes. Agent checked; human verification pending.',conf='restricted')
save(E/'source_manifest.json',{'schema_version':'1.0','sources':sources})
save(E/'local-evidence-index.json',index)
claims=[]; section='Abstract'
def claim(cid,kind,text,evidence,section):
    norm=' '.join(text.split())
    claims.append(dict(claim_id=cid,section=section,claim_kind=kind,claim_text_sha256=hashlib.sha256(norm.encode()).hexdigest(),evidence_ids=';'.join(evidence),verification_status='unverified',uncertainty='not_estimated',analysis_intent='descriptive'))
claim('C000','result',m['abstract'],['E101','E102','E103','E104','E109'],'Abstract')
for b in m['blocks']:
    if b['type']=='h1': section=b['text']
    if 'id' in b: claim(b['id'],'result' if section.startswith('V.') else 'factual',b['text'],b['evidence'],section)
    elif b['type'] in ['equation','table','figure']:
        cid=f'C{len(claims):03}'
        # Paragraph IDs are already fixed through C041; displays use C042 onward.
        cid=f'C{42+sum(1 for c in claims if int(c["claim_id"][1:])>=42):03}'
        if b['type']=='equation':
            evidence=['E102'] if b['number']<4 else ['E103']; text=b['text']
        elif b['type']=='table':
            evidence=['E101','E103','E008']; text=json.dumps({k:v for k,v in b.items() if k not in ['claim_id','evidence']},sort_keys=True,ensure_ascii=False)
        else:
            fp=read(P/'figures/figure-provenance.json'); fig=next(x for x in fp['figures'] if x['figure_id'].split('_',1)[1]==b['figure'])
            evidence=[{1:'E101',2:'E102',3:'E103',4:'E103',5:'E103'}[b['number']]];text=fig['caption']
        claim(cid,'numeric',text,evidence,section)
        b['claim_id']=cid;b['evidence']=evidence
save(P/'src/manuscript.json',m)
with (E/'claims.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(claims[0]));w.writeheader();w.writerows(claims)
h=read(ROOT/'simulations/results/hardware-summary.json')
values=[('baseline_lamp_h',h['baseline']['runtime_to_common_endpoint_h'],'h'),('priority_lamp_h',h['priority']['runtime_to_common_endpoint_h'],'h'),('priority_fan_h',h['priority']['fan_service_h'],'h'),('lamp_gain_percent',h['runtime_extension_pct'],'percent'),('fan_loss_percent',100*(1-h['priority']['fan_service_h']/h['baseline']['fan_service_h']),'percent'),('baseline_energy_wh',h['baseline']['delivered_energy_wh'],'Wh'),('priority_energy_wh',h['priority']['delivered_energy_wh'],'Wh'),('sensitivity_pairs',len(h['sensitivity_pairs']),'cases'),('startup_cases',len(h['startup_cases']),'cases')]
facts=[]
for concept,v,unit in values:
    for loc in ['Results','Evidence registry']:
        facts.append(dict(fact_id=f'N{len(facts)+1:03}',concept=concept,value=v,unit=unit,section=loc,analysis_set='deterministic simulation',numerator=None,denominator=None,sample_size=None,evidence_ids=['E103']))
methods=[]; results=[]
for i,(name,count) in enumerate([('Nominal deterministic paired discharge',1),('Deterministic paired sensitivity scenarios',18),('Separate behavioral startup scenarios',6)],1):
    mid=f'M{i:03}';oid=f'O{i:03}'
    methods.append(dict(method_id=mid,name=name,analysis_intent='descriptive',protocol_status='not_applicable',outcome_ids=[oid]))
    results.append(dict(result_id=f'R{i:03}',method_id=mid,outcome_id=oid,analysis_intent='descriptive',sample_size=count,evidence_ids=['E103'],reported_sections=['Abstract','V. Results']))
save(E/'consistency_manifest.json',dict(schema_version='1.0',numeric_facts=facts,methods=methods,results=results))
skillroot=skill.parent
a=read(skillroot/'assets/authorship_template.json')
template=a['authors'][0]
a['authors']=[dict(template,author_id=f'A{i+1:03}',name=n) for i,n in enumerate(m['authors'])]
a['ai_use'].update(used=True,tools=[dict(name='Codex',version='GPT-6-based session; desktop build not recorded',provider='OpenAI',purpose='Project artifact assistance, literature retrieval, evidence checks, drafting and figure code',materials_sent='source_documents',external_service=True,explicit_authorization=True,policy_reviewed=False)],disclosed_in=['other'])
save(E/'authorship.json',a)
manifest=read(skillroot/'assets/manuscript_manifest_template.json')
manifest.update(document_id='wattsense-design-simulation-2026-09-30',study_design='descriptive engineering design and deterministic simulation study')
save(E/'manuscript_manifest.json',manifest)
save(E/'reporting_coverage.json',dict(study_design=manifest['study_design'],clinical_guidelines_applicable=False,rationale='No human, animal, clinical, diagnostic or systematic-review study. No target venue supplied.',covered=['question','architecture','assumptions','equations','scenario matrix','both-load tradeoff','negative startup results','numerical verification','limitations','planned measurements'],pending=['human evidence review','affiliations','venue instructions','contributions','funding/conflicts','institutional similarity review']))
snapshot=E/'run-2026-09-30';snapshot.mkdir(exist_ok=True)
for filename in ['suite-summary.json','hardware-summary.json','system-summary.json','spice-summary.json','firmware-host-summary.json','python-tests.log']:
    shutil.copy2(ROOT/'simulations/results'/filename,snapshot/filename)
for e,(_,paths) in local.items(): index[e]=[dict(path=x,sha256=sha(ROOT/x)) for x in paths]
save(E/'local-evidence-index.json',index)
print('Prepared evidence records. Human verification and submission approval remain false.')
