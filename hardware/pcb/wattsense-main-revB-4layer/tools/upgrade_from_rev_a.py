"""One-time Rev A -> B migration. Refuses to overwrite an existing 4-layer board.
Use KiCad's Python. Native CAD remains authoritative after this migration.
"""
from pathlib import Path
import hashlib, json, math
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'wattsense-main.kicad_pcb'
b = p.LoadBoard(str(FILE))
assert b.GetCopperLayerCount() == 2, 'Migration already applied; do not overwrite manual edits'
source_hash = hashlib.sha256(FILE.read_bytes()).hexdigest()
b.SetCopperLayerCount(4)
vec = lambda x,y: p.VECTOR2I(p.FromMM(x), p.FromMM(y))
gnd = next(a.GetNetCode() for f in b.GetFootprints() for a in f.Pads() if a.GetNetname() == '/GND')
for layer in [p.In1_Cu, p.In2_Cu]:
    z = p.ZONE(b)
    z.SetLayer(layer); z.SetNetCode(gnd)
    z.SetLocalClearance(p.FromMM(.25)); z.SetMinThickness(p.FromMM(.2))
    z.SetPadConnection(p.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(p.FromMM(.3)); z.SetThermalReliefSpokeWidth(p.FromMM(.5))
    poly = z.Outline(); poly.NewOutline()
    for x,y in [(50.7,50.7),(149.3,50.7),(149.3,139.3),(50.7,139.3)]:
        poly.Append(p.FromMM(x),p.FromMM(y))
    b.Add(z)

def point_segment(x,y,a,c):
    ax,ay=p.ToMM(a.x),p.ToMM(a.y); cx,cy=p.ToMM(c.x),p.ToMM(c.y)
    dx,dy=cx-ax,cy-ay
    t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return math.hypot(x-ax-t*dx,y-ay-t*dy)

def safe(x,y):
    pos=vec(x,y)
    # Keep added vias out of all component bodies/pads and mounting holes.
    for f in b.GetFootprints():
        bb=f.GetBoundingBox(False,False); bb.Inflate(p.FromMM(.8))
        if bb.Contains(pos): return False
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            if math.hypot(x-p.ToMM(t.GetPosition().x),y-p.ToMM(t.GetPosition().y)) < 1.1: return False
        elif t.GetNetCode()!=gnd and point_segment(x,y,t.GetStart(),t.GetEnd()) < .35+p.ToMM(t.GetWidth())/2+.3:
            return False
    return True

added=[]
points=[(x,y) for x in range(54,148,10) for y in range(54,138,10)]
# Additional local connections around sensor decoupling and the fan ground return.
points += [(76.8,82),(106.8,82),(137.8,82),(123.5,111.3),(122,109.8),(124,113),
           (68,80),(98,80),(129,80),(75,85),(105,85),(136,85)]
for x,y in points:
    if not safe(x,y): continue
    v=p.PCB_VIA(b); v.SetPosition(vec(x,y)); v.SetWidth(p.FromMM(.7)); v.SetDrill(p.FromMM(.35))
    v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNetCode(gnd); b.Add(v)
    added.append({'uuid':v.m_Uuid.AsString(),'xy_mm':[x,y]})
for d in b.GetDrawings():
    if isinstance(d,p.PCB_TEXT) and d.GetText()=='WATTSENSE  /  REV A':
        d.SetText('WATTSENSE / REV B / 4L')
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(FILE),b)
# SWIG does not expose the stackup descriptor. Insert a native stackup, then
# reload and save through KiCad to verify syntax and retain native formatting.
stack='''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "prepreg") (thickness 0.18) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 2" (type "core") (thickness 1.115) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 3" (type "prepreg") (thickness 0.18) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "ENIG") (dielectric_constraints no))'''
text=FILE.read_text(); assert '(stackup' not in text
FILE.write_text(text.replace('(setup','(setup\n'+stack,1))
b=p.LoadBoard(str(FILE)); p.SaveBoard(str(FILE),b)
manifest=json.loads((ROOT/'design.json').read_text()); manifest['revision']='B'; manifest['copper_layers']=4
(ROOT/'design.json').write_text(json.dumps(manifest,indent=2))
sch=ROOT/'wattsense-main.kicad_sch'
sch.write_text(sch.read_text().replace('(rev "A")','(rev "B")').replace('(date "2026-09-27")','(date "2026-09-28")'))
(ROOT/'reports/revision-migration.json').write_text(json.dumps({'source_revA_pcb_sha256':source_hash,'added_ground_vias':added,'stackup':'F.Cu / In1.Cu GND / In2.Cu GND / B.Cu','note':'Nominal dielectric dimensions; fabricator stackup confirmation pending.'},indent=2))
print(f'Created four-layer Rev B with {len(added)} new GND stitching vias. Run DRC before use.')
