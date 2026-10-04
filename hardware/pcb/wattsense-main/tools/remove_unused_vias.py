"""Remove single-layer-only vias and their unused initial SOIC escape stubs.
Only objects reported by KiCad DRC are considered. Rerun DRC afterwards.
"""
import json
from pathlib import Path
import pcbnew as p
root=Path(__file__).resolve().parents[1]
report=json.loads((root/'reports/drc.json').read_text())
ids={item['uuid'] for v in report['violations'] if v['type']=='via_dangling' for item in v['items']}
stubs={item['uuid'] for v in report['violations'] if v['type']=='track_dangling' for item in v['items']}
b=p.LoadBoard(str(root/'wattsense-main.kicad_pcb'))
n=0
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in ids:
        b.Remove(t);n+=1
    elif not isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in stubs:
        assert 1.90<p.ToMM(t.GetLength())<1.95,'Not one of the initial SOIC escape stubs; inspect manually'
        b.Remove(t);n+=1
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(root/'wattsense-main.kicad_pcb'),b)
print(f'Removed {n} unused via/stub objects. Fresh DRC is required.')
