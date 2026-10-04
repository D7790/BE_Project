"""Check explicit high-current track paths, independent of net labels and pours.

This checks layout width continuity, not physical ampacity or thermal behavior.
Run with KiCad Python after the normal CAD audit.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json
import pcbnew as p
root=Path(__file__).resolve().parents[1]
source=root/'wattsense-main.kicad_pcb'
board=p.LoadBoard(str(source))
def point(v):return (v.x,v.y)
def pad(name):
    ref,number=name.split('.')
    return board.FindFootprintByReference(ref).FindPadByNumber(number)
def check(a,b,width):
    first,last=pad(a),pad(b)
    assert first.GetNetCode()==last.GetNetCode(),(a,b,'different nets')
    edges=defaultdict(set)
    for t in board.GetTracks():
        if isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.F_Cu or t.GetNetCode()!=first.GetNetCode():continue
        if p.ToMM(t.GetWidth())+1e-6<width:continue
        x,y=point(t.GetStart()),point(t.GetEnd());edges[x].add(y);edges[y].add(x)
    seen={point(first.GetPosition())};queue=list(seen)
    while queue:
        for nxt in edges[queue.pop()]:
            if nxt not in seen:seen.add(nxt);queue.append(nxt)
    assert point(last.GetPosition()) in seen,(a,b,'missing explicit track path',width)
    return {'from':a,'to':b,'net':first.GetNetname(),'minimum_track_width_mm':width,'layer':'F.Cu','status':'PASS'}
wide=[('J1.1','R1.1'),('J2.1','R3.1'),('R2.2','J3.1'),('R1.2','R3.2'),
      ('R3.2','R2.1'),('R3.2','D2.1'),('J4.1','F1.1'),('F1.2','F2.1'),
      ('F2.1','F3.1'),('F2.2','J5.1'),('F3.2','J6.1'),('J6.1','D1.1'),
      ('J1.2','J2.2'),('J2.2','J3.2'),('J3.2','J4.2'),('J4.2','J5.2'),('D2.2','J2.2')]
checks=[check(a,b,1.5) for a,b in wide]
checks += [check('J6.2','D1.2',1.2),check('D1.2','Q1.3',.65),check('J5.2','Q1.2',.6)]
result={'status':'PASS','scope':'20 explicit front-copper power/return paths; no reliance on a signal via or GND pour to pass this check. Not an ampacity calculation.',
        'pcb_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'paths':checks}
(root/'reports/power-path-audit.json').write_text(json.dumps(result,indent=2))
print('PASS: 20 explicit power/return track paths at their documented minimum widths.')
