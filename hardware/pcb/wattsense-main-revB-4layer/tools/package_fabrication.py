"""Package exactly the reviewed fabrication layers; no stale extras."""
from pathlib import Path
import csv, hashlib, json, re, zipfile
root=Path(__file__).resolve().parents[1]
audit=json.loads((root/'reports/connectivity-audit.json').read_text())
assert audit['status']=='PASS'
for name,digest in audit['sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,f'Changed checked source: {name}'
assert audit['copper_layers']==4
power_audit=json.loads((root/'reports/power-path-audit.json').read_text())
assert power_audit['status']=='PASS' and power_audit['pcb_sha256']==audit['sha256']['wattsense-main.kicad_pcb']
assert power_audit['script_sha256']==hashlib.sha256((root/'tools/check_power_paths.py').read_bytes()).hexdigest()
names=['F_Cu.gtl','In1_Cu.g1','In2_Cu.g2','B_Cu.gbl','F_Mask.gts','B_Mask.gbs','F_Silkscreen.gto','B_Silkscreen.gbo','Edge_Cuts.gm1','job.gbrjob','PTH.drl','NPTH.drl']
paths=[root/'exports/gerbers'/('wattsense-main-'+name) for name in names]
for file in paths:assert file.exists() and file.stat().st_size>100,file
for file in paths:
    content=file.read_text()
    if file.suffix=='.drl':
        assert 'METRIC' in content
        coords=re.findall(r'^X(-?[0-9.]+)Y(-?[0-9.]+)$',content,re.M)
        for x,y in coords:
            # KiCad Excellon Y is negative of PCB view Y with absolute origin.
            assert 50<float(x)<150 and -140<float(y)<-50,(file,x,y)
        expected=4 if 'NPTH' in file.name else audit['vias']+33
        assert len(coords)==expected,(file,len(coords),expected)
    elif file.suffix!='.gbrjob':assert '%MOMM*%' in content and 'M02*' in content,file
out=root/'exports/wattsense-main-revB-4layer-prototype.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for file in paths:z.write(file,file.name)
    z.write(root/'FABRICATION.md','FABRICATION.md')
    z.writestr('SOURCE-VALIDATION.json',json.dumps(audit,indent=2))
    z.writestr('POWER-PATH-VALIDATION.json',json.dumps(power_audit,indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None

groups={}
with (root/'BOM.csv').open(newline='') as f:
    for row in csv.DictReader(f):
        key=(row['Value'],row['Manufacturer_part'],row['Footprint'])
        groups.setdefault(key,[]).append(row['Reference'])
with (root/'BOM-grouped.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Quantity','References','Value','Manufacturer_part','Footprint'])
    for key,refs in groups.items():w.writerow([len(refs),', '.join(refs),*key])
print(f'Checked and packaged {len(paths)} fabrication files; {out.name}')
