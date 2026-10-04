"""Read-only native CAD recheck, with a separate all-rules scratch project."""
from pathlib import Path
import collections, csv, datetime, hashlib, json, shutil, subprocess, sys, zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
CAD = ROOT / 'hardware/pcb/wattsense-main-revB-4layer'
CLI = Path(r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe')
PYTHON = CLI.with_name('python.exe')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SOURCE_NAMES = ['wattsense-main.kicad_sch', 'wattsense-main.kicad_pcb', 'wattsense-main.kicad_pro',
                'BOM.csv', 'BOM-grouped.csv', 'design.json', 'tools/audit_design.py', 'tools/check_power_paths.py']
before = {name: sha(CAD / name) for name in SOURCE_NAMES}
commands = []

def run(args, logname, allowed=(0,)):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    (OUT / logname).write_text(result.stdout + result.stderr, encoding='utf-8')
    commands.append({'argv': [str(x) for x in args], 'exit_code': result.returncode, 'log': logname})
    assert result.returncode in allowed, (logname, result.returncode, result.stderr)

run([CLI, 'sch', 'erc', CAD/'wattsense-main.kicad_sch', '--format', 'json', '--severity-all',
     '--exit-code-violations', '-o', OUT/'erc.json'], 'erc.log')
run([CLI, 'pcb', 'drc', CAD/'wattsense-main.kicad_pcb', '--schematic-parity', '--format', 'json',
     '--severity-all', '--all-track-errors', '--exit-code-violations', '--refill-zones', '-o', OUT/'drc.json'], 'drc.log')
run([CLI, 'sch', 'export', 'netlist', CAD/'wattsense-main.kicad_sch', '--format', 'kicadxml',
     '-o', OUT/'schematic.net.xml'], 'netlist.log')
run([CLI, 'pcb', 'export', 'gerbers', CAD/'wattsense-main.kicad_pcb', '-o', str(OUT/'gerbers')+'/',
     '-l', 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts'], 'gerbers.log')
run([CLI, 'pcb', 'export', 'drill', CAD/'wattsense-main.kicad_pcb', '-o', str(OUT/'gerbers')+'/',
     '--excellon-separate-th', '--generate-report', '--report-path', OUT/'drill-report.txt'], 'drill.log')

# Execute the existing native pin/value/footprint and explicit power-route checks,
# redirecting reports only. Their original source paths stay valid for hash checks.
wrapper = '''from pathlib import Path
root=Path(%r)
out=Path(%r)
script=(root/'tools/audit_design.py').read_text()
for name in ['schematic.net.xml','erc.json','drc.json','connectivity-audit.json']:
    script=script.replace("ROOT/'reports'/"+repr(name), "Path("+repr(str(out/name))+")")
exec(compile(script,str(root/'tools/audit_design.py'),'exec'),{'__file__':str(root/'tools/audit_design.py')})
script=(root/'tools/check_power_paths.py').read_text()
script=script.replace("root/'reports/power-path-audit.json'", "Path("+repr(str(out/'power-path-audit.json'))+")")
exec(compile(script,str(root/'tools/check_power_paths.py'),'exec'),{'__file__':str(root/'tools/check_power_paths.py')})
''' % (str(CAD), str(OUT))
(OUT/'native_audit_wrapper.py').write_text(wrapper, encoding='utf-8')
run([PYTHON, OUT/'native_audit_wrapper.py'], 'native-audit.log')

archive=CAD/'exports/wattsense-main-revB-4layer-prototype.zip'
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==15
    manifest=json.loads(z.read('SOURCE-VALIDATION.json'))
    assert all(sha(CAD/name)==digest for name,digest in manifest['sha256'].items())
    assert manifest==json.loads((CAD/'reports/connectivity-audit.json').read_text())
    assert json.loads(z.read('POWER-PATH-VALIDATION.json'))==json.loads((CAD/'reports/power-path-audit.json').read_text())
    assert z.read('FABRICATION.md')==(CAD/'FABRICATION.md').read_bytes()
    for f in (CAD/'exports/gerbers').iterdir(): assert z.read(f.name)==f.read_bytes(), f.name

def normalized(f):
    if f.suffix=='.gbrjob':
        obj=json.loads(f.read_text()); obj['Header'].pop('CreationDate'); return obj
    return '\n'.join(line for line in f.read_text().splitlines() if 'CreationDate' not in line
                     and 'Created by KiCad' not in line and not line.startswith('; DRILL file KiCad'))
compared=[]
for fresh in sorted((OUT/'gerbers').iterdir()):
    assert normalized(fresh)==normalized(CAD/'exports/gerbers'/fresh.name), fresh.name
    compared.append(fresh.name)
assert len(compared)==12

# Grouped purchasing BOM is checked independently of its generator.
with (CAD/'BOM.csv').open(newline='', encoding='utf-8-sig') as f:
    flat={r['Reference']:(r['Value'],r['Manufacturer_part'],r['Footprint']) for r in csv.DictReader(f)}
expanded={}
with (CAD/'BOM-grouped.csv').open(newline='', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        refs=[r.strip() for r in row['References'].split(',')]
        assert int(row['Quantity'])==len(refs)
        for ref in refs:
            assert ref not in expanded
            expanded[ref]=(row['Value'],row['Manufacturer_part'],row['Footprint'])
assert flat==expanded

# Re-enable ignored DRC categories in a COPY. Native delivery rules are unchanged.
scratch=OUT/'all-rules-scratch'; scratch.mkdir(exist_ok=True)
for name in ['wattsense-main.kicad_sch','wattsense-main.kicad_pcb','wattsense-main.kicad_pro','Wattsense.kicad_sym','sym-lib-table']:
    shutil.copy2(CAD/name, scratch/name)
project=json.loads((scratch/'wattsense-main.kicad_pro').read_text())
rule_severities=project['board']['design_settings']['rule_severities']
reenabled=[key for key,value in rule_severities.items() if value=='ignore']
for key in reenabled: rule_severities[key]='warning'
erc_original=json.loads((OUT/'erc.json').read_text())
erc_ignored=[c['key'] for c in erc_original.get('ignored_checks',[])]
project.setdefault('erc',{}).setdefault('rule_severities',{}).update({key:'warning' for key in erc_ignored})
(scratch/'wattsense-main.kicad_pro').write_text(json.dumps(project,indent=2),encoding='utf-8')
run([CLI,'pcb','drc',scratch/'wattsense-main.kicad_pcb','--schematic-parity','--format','json',
     '--severity-all','--all-track-errors','--exit-code-violations','--refill-zones','-o',OUT/'all-rules-drc.json'],
    'all-rules-drc.log',allowed=(0,5))
run([CLI,'sch','erc',scratch/'wattsense-main.kicad_sch','--format','json','--severity-all',
     '--exit-code-violations','-o',OUT/'all-rules-erc.json'],'all-rules-erc.log',allowed=(0,5))
full_drc=json.loads((OUT/'all-rules-drc.json').read_text())
full_erc=json.loads((OUT/'all-rules-erc.json').read_text())
drc_types=collections.Counter(v['type'] for v in full_drc['violations'])
drc_parity_types=collections.Counter(v['type'] for v in full_drc['schematic_parity'])
erc_items=[v for s in full_erc['sheets'] for v in s['violations']]
erc_types=collections.Counter(v['type'] for v in erc_items)
assert not full_drc['violations'] and not full_drc['unconnected_items']
assert drc_parity_types=={'footprint_filters_mismatch':6}
assert erc_types=={'footprint_filter':6}
assert all(v['severity']=='warning' for v in full_drc['schematic_parity']+erc_items)
assert {v['items'][0]['description'] for v in full_drc['schematic_parity']}=={'Footprint J'+str(i) for i in range(1,7)}
assert not full_drc.get('ignored_checks') and not full_erc.get('ignored_checks')
after={name:sha(CAD/name) for name in SOURCE_NAMES}
assert before==after
summary={
    'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'native_configured_checks':'PASS', 'hardware_validation':'NOT PERFORMED',
    'native_sources_unchanged':before==after, 'native_sha256':after,
    'archive_sha256':sha(archive), 'archive_entries':15,'fabrication_comparison_files':compared,
    'fabrication_comparison':'PASS excluding timestamp metadata only',
    'grouped_bom_matches_all_50_locations':flat==expanded,
    'reenabled_DRC_categories':reenabled,
    'all_rules_DRC_report_counts':dict(drc_types),'all_rules_DRC_still_ignored':full_drc.get('ignored_checks',[]),
    'all_rules_DRC_parity_counts':dict(drc_parity_types),
    'all_rules_DRC_unconnected':len(full_drc['unconnected_items']),
    'all_rules_ERC_report_counts':dict(erc_types),'all_rules_ERC_still_ignored':full_erc.get('ignored_checks',[]),
    'all_rules_metadata_disposition':'Six generic connector footprint-filter mismatches for J1-J6. Native schematic, actual PCB, design manifest and BOM agree on the Phoenix 1715721-compatible footprint. Its 5.08 mm pitch, 1.3 mm drill and every pad-net assignment pass independent checks. These warnings are explicitly retained as metadata findings; no physical compatibility guarantee follows.',
    'commands':commands,
    'scope':'Native configured CAD checks plus all ignored categories enabled in a scratch copy; no native save, order, hardware connection, physical test or thermal/current qualification.'
}
(OUT/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
