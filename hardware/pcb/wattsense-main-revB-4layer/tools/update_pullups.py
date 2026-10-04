"""One-time Rev B pullup change motivated by the capacitance sweep."""
from pathlib import Path
import csv,json
import pcbnew as p
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'design.json').read_text())
for part in manifest['parts']:
    if part['ref'] in ('R4','R5'):
        assert part['value']=='4.7k','Already updated; use native CAD for subsequent edits'
        part.update(value='2.2k',mpn='RC0805FR-072K2L',note='Rev B: 100 kHz I2C pullup, checked through 400 pF in reduced RC simulation.')
(root/'design.json').write_text(json.dumps(manifest,indent=2))
path=root/'wattsense-main.kicad_sch'; lines=path.read_text().splitlines(); count=0
for i,line in enumerate(lines):
    if line.startswith('(symbol (lib_id ') and any(f'(property "Reference" "{ref}"' in line for ref in ['R4','R5']):
        assert '(property "Value" "4.7k"' in line
        lines[i]=line.replace('(property "Value" "4.7k"','(property "Value" "2.2k"'); count+=1
assert count==2; path.write_text('\n'.join(lines)+'\n')
b=p.LoadBoard(str(root/'wattsense-main.kicad_pcb'))
for f in b.GetFootprints():
    if f.GetReference() in ['R4','R5']: f.SetValue('2.2k')
p.SaveBoard(str(root/'wattsense-main.kicad_pcb'),b)
with (root/'BOM.csv').open(newline='') as f: reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
for row in rows:
    if row['Reference'] in ['R4','R5']:
        row.update(Value='2.2k',Manufacturer_part='RC0805FR-072K2L',Notes='Rev B 100 kHz I2C pullup; see simulation report.')
with (root/'BOM.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
print('Updated R4/R5 in schematic, PCB, manifest and component BOM.')
