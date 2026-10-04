"""Two-layer grid routing with explicit power paths and shunt sense takeoffs.

The router is only a construction tool. KiCad DRC and an independent net audit
are mandatory after construction; routing success is not electrical validation.
"""
from pathlib import Path
import heapq, math, time
import numpy as np
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'wattsense-main.kicad_pcb'
STEP=.2
X0,Y0=50.,50.
NX,NY=501,451
board=p.LoadBoard(str(FILE))
fps={f.GetReference():f for f in sorted(board.GetFootprints(),key=lambda f:f.GetReference())}
pads={(ref,a.GetNumber()):a for ref,f in fps.items() for a in f.Pads() if a.GetNumber()}
objects=[]
via_positions=[]
def mm(v): return p.ToMM(v)
def coord(pad): return (mm(pad.GetPosition().x),mm(pad.GetPosition().y))
def at(ref):
    r,n=ref.split('.'); return pads[r,n]
def gi(x,y): return (round((x-X0)/STEP),round((y-Y0)/STEP))
def pos(x,y): return (X0+x*STEP,Y0+y*STEP)
def vec(xy): return p.VECTOR2I(*[p.FromMM(v) for v in xy])

for f in board.GetFootprints():
    for pad in f.Pads():
        box=pad.GetBoundingBox(); x0,y0=mm(box.GetX()),mm(box.GetY()); x1,y1=x0+mm(box.GetWidth()),y0+mm(box.GetHeight())
        layers=[0,1] if pad.GetAttribute()!=p.PAD_ATTRIB_SMD else [0]
        objects.append(('rect',layers,pad.GetNetCode(),(x0,y0,x1,y1)))
# Include the full insulating mounting-hole keepout, not just the drill.
for f in board.GetFootprints():
    if f.GetReference().startswith('H'):
        x,y=mm(f.GetPosition().x),mm(f.GetPosition().y)
        objects.append(('circle',[0,1],-1,(x,y,3.4)))

def raster(net,width):
    blocked=np.zeros((2,NY,NX),dtype=bool)
    margin=.24+width/2+STEP*.55
    edge=.5+width/2+STEP
    xx=X0+np.arange(NX)*STEP; yy=Y0+np.arange(NY)*STEP
    blocked[:,:,xx<X0+edge]=True; blocked[:,:,xx>150-edge]=True
    blocked[:,yy<Y0+edge,:]=True; blocked[:,yy>140-edge,:]=True
    for kind,layers,n,data in objects:
        if n==net: continue
        if kind=='rect':
            x0,y0,x1,y1=data; xa,xb=x0-margin,x1+margin; ya,yb=y0-margin,y1+margin
        elif kind=='circle':
            x,y,r=data; radius=r+margin; xa,xb=x-radius,x+radius; ya,yb=y-radius,y+radius
        else:
            x0,y0,x1,y1,w=data; radius=w/2+margin; xa,xb=min(x0,x1)-radius,max(x0,x1)+radius; ya,yb=min(y0,y1)-radius,max(y0,y1)+radius
        a=max(0,int(math.floor((xa-X0)/STEP))); b=min(NX,int(math.ceil((xb-X0)/STEP))+1)
        c=max(0,int(math.floor((ya-Y0)/STEP))); d=min(NY,int(math.ceil((yb-Y0)/STEP))+1)
        if a>=b or c>=d: continue
        if kind=='rect':
            for layer in layers: blocked[layer,c:d,a:b]=True
        else:
            gx=xx[a:b][None,:]; gy=yy[c:d][:,None]
            if kind=='circle': mask=(gx-x)**2+(gy-y)**2<=radius**2
            else:
                dx,dy=x1-x0,y1-y0; length=dx*dx+dy*dy
                t=np.clip(((gx-x0)*dx+(gy-y0)*dy)/max(length,1e-12),0,1)
                mask=(gx-(x0+t*dx))**2+(gy-(y0+t*dy))**2<=radius**2
            for layer in layers: blocked[layer,c:d,a:b]|=mask
    return blocked

def segment(a,b,net,width,layer):
    if math.dist(a,b)<1e-5:return
    t=p.PCB_TRACK(board); t.SetStart(vec(a)); t.SetEnd(vec(b)); t.SetWidth(p.FromMM(width)); t.SetLayer(p.F_Cu if layer==0 else p.B_Cu); t.SetNetCode(net); board.Add(t)
    objects.append(('line',[layer],net,(*a,*b,width)))
def via(xy,net):
    if any(n==net and math.dist(xy,v)<.01 for v,n in via_positions):return
    v=p.PCB_VIA(board);v.SetPosition(vec(xy));v.SetWidth(p.FromMM(.7));v.SetDrill(p.FromMM(.35));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net);board.Add(v)
    objects.append(('circle',[0,1],net,(*xy,.35)))
    via_positions.append((xy,net))

done=[]
def route(a,b,width=.25,front=False):
    pa,pb=at(a),at(b); net=pa.GetNetCode(); assert net==pb.GetNetCode(),(a,b)
    startxy,endxy=coord(pa),coord(pb); sx,sy=gi(*startxy);tx,ty=gi(*endxy)
    blocked=raster(net,width)
    vias=raster(net,.7) if not front else None
    if vias is not None:
        # Do not drill into any solder pad, including a pad on the same net.
        for kind,layers,n,data in objects:
            if kind!='rect':continue
            x0,y0,x1,y1=data; margin=.35+.25
            ia=max(0,int(math.floor((x0-margin-X0)/STEP)));ib=min(NX,int(math.ceil((x1+margin-X0)/STEP))+1)
            ic=max(0,int(math.floor((y0-margin-Y0)/STEP)));id_=min(NY,int(math.ceil((y1+margin-Y0)/STEP))+1)
            vias[:,ic:id_,ia:ib]=True
        for (vx,vy),n in via_positions:
            # Same-net holes still require fabrication clearance. Reuse the
            # exact existing via instead of placing another drill nearby.
            ix,iy=gi(vx,vy)
            for xx in range(max(0,ix-4),min(NX,ix+5)):
                for yy in range(max(0,iy-4),min(NY,iy+5)):
                    if math.dist(pos(xx,yy),(vx,vy))<.7:vias[:,yy,xx]=True
            if n==net:vias[:,iy,ix]=False
    starts=[0] if front or pa.GetAttribute()==p.PAD_ATTRIB_SMD else [0,1]
    ends=[0] if front or pb.GetAttribute()==p.PAD_ATTRIB_SMD else [0,1]
    for l in starts:
        if blocked[l,sy,sx]: raise RuntimeError(f'Blocked source {a} width {width}')
    for l in ends:
        if blocked[l,ty,tx]: raise RuntimeError(f'Blocked target {b} width {width}')
    size=NX*NY
    def enc(x,y,l):return l*size+y*NX+x
    def dec(z):l,t=divmod(z,size);y,x=divmod(t,NX);return x,y,l
    goals={enc(tx,ty,l) for l in ends}
    costs={}; prev={};heap=[]
    for l in starts:
        z=enc(sx,sy,l);costs[z]=0;heapq.heappush(heap,(abs(tx-sx)+abs(ty-sy),0,z))
    found=None; count=0
    while heap:
        _,g,z=heapq.heappop(heap)
        if g!=costs[z]: continue
        if z in goals: found=z;break
        x,y,l=dec(z);count+=1
        opts=[]
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            xx,yy=x+dx,y+dy
            if xx<0 or xx>=NX or yy<0 or yy>=NY or blocked[l,yy,xx]:continue
            if dx and dy and (blocked[l,y,xx] or blocked[l,yy,x]):continue
            opts.append((xx,yy,l,1.414214 if dx and dy else 1.0))
        if not front and not blocked[1-l,y,x] and not vias[0,y,x] and not vias[1,y,x]: opts.append((x,y,1-l,12.0))
        for xx,yy,ll,c in opts:
            nz=enc(xx,yy,ll);ng=g+c
            if ng<costs.get(nz,1e30):
                costs[nz]=ng;prev[nz]=z;dx,dy=abs(tx-xx),abs(ty-yy)
                h=max(dx,dy)+.414214*min(dx,dy)
                heapq.heappush(heap,(ng+h,ng,nz))
    if found is None: raise RuntimeError(f'No path {a} -> {b}, width={width}, visited={count}')
    path=[found]
    while path[-1] in prev:path.append(prev[path[-1]])
    path=[dec(z) for z in path[::-1]]
    # Collapse collinear grid runs; preserve every actual layer transition.
    short=[path[0]]
    for i in range(1,len(path)-1):
        aa,bb,cc=path[i-1],path[i],path[i+1]
        if (bb[0]-aa[0],bb[1]-aa[1],bb[2]-aa[2])!=(cc[0]-bb[0],cc[1]-bb[1],cc[2]-bb[2]):short.append(bb)
    short.append(path[-1])
    segment(startxy,pos(*short[0][:2]),net,width,short[0][2])
    for s,t in zip(short,short[1:]):
        if s[2]!=t[2]:via(pos(*s[:2]),net)
        else:segment(pos(*s[:2]),pos(*t[:2]),net,width,s[2])
    segment(pos(*short[-1][:2]),endxy,net,width,short[-1][2])
    done.append((a,b,width));print(f'{a:7} -> {b:7} {width:.2f} mm  {len(short)} segments',flush=True)

# Give the closely spaced SOIC supply/digital pads their own short escape to
# an off-pad via. This preserves access before the shunt/power routes are laid.
for i in [1,2,3]:
    for pin in ['1','2','3','4','5','6']:
        pad=at(f'U{i}.{pin}');x,y=coord(pad)
        gx,gy=gi(x,88.4 if pin in ['1','2','3','4'] else 79.6)
        target=pos(gx,gy)
        segment((x,y),target,pad.GetNetCode(),.25,0)
        via(target,pad.GetNetCode())

# Escape the small MOSFET gate before its larger adjacent current paths.
route('R7.2','Q1.1',.25,True)
route('R8.1','Q1.1',.25,True)
# Fixed power topology, no power-current layer changes.
power=[('J1.1','R1.1'),('J2.1','R3.1'),('R2.2','J3.1'),('R1.2','R3.2'),('R3.2','R2.1'),('R3.2','D2.1'),('J4.1','F1.1'),('F1.2','F2.1'),('F2.1','F3.1'),('F2.2','J5.1'),('F3.2','J6.1'),('J6.1','D1.1')]
for a,b in power:route(a,b,1.5,True)
route('J6.2','D1.2',1.2,True)
route('D1.2','Q1.3',.65,True)
# Ground copper paths back each high-current terminal, reinforced by both pours.
for a,b in [('J1.2','J2.2'),('J2.2','J3.2'),('J3.2','J4.2'),('J4.2','J5.2')]:route(a,b,1.5,True)
route('D2.2','J2.2',1.5,True)
route('J5.2','Q1.2',.6,True)
# Kelvin-style takeoffs MUST originate on resistor pads, never at power terminals.
for i in [1,2,3]:route(f'U{i}.5',f'C{i}.1',.25,True)
for i in [1,2,3]:
    route(f'U{i}.8',f'C{i+7}.1',.25)
    route(f'U{i}.7',f'C{i+7}.2',.25)
    route(f'R{i}.1',f'U{i}.8',.25)
    route(f'R{i}.2',f'U{i}.7',.25)

# Route the local supply/address straps before long I2C tracks can fence in
# their SOIC pads. These paths only carry IC supply / address-input currents.
for a,b in [('U2.2','U2.5'),('U3.1','U3.5'),('U1.1','U1.2'),('U1.2','U1.6'),('U2.1','U2.6'),('U3.2','U3.6'),('U1.6','C1.2'),('U2.6','C2.2'),('U3.6','C3.2')]:
    route(a,b,.25)

# Complete each net using nearest remaining pad pairs; explicit power and sense
# connections above seed the connectivity tree. Ground signals use 0.35 mm.
groups={}
for key,pad in pads.items(): groups.setdefault(pad.GetNetCode(),[]).append('.'.join(key))
parent={a:a for vals in groups.values() for a in vals}
def root(a):
    while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
    return a
def join(a,b):parent[root(a)]=root(b)
for a,b,w in done:join(a,b)
order=sorted(groups,key=lambda n:(at(groups[n][0]).GetNetname().lstrip('/') in ['GND','3V3'],len(groups[n])))
for net in order:
    vals=groups[net]
    if net<=0:continue
    while len({root(a) for a in vals})>1:
        pairs=sorted((math.dist(coord(at(a)),coord(at(b))),a,b) for j,a in enumerate(vals) for b in vals[j+1:] if root(a)!=root(b))
        error=None
        for _,a,b in pairs:
            try:route(a,b,.35 if at(a).GetNetname().lstrip('/') in ['GND','3V3','5V','ESP_5V'] else .25);join(a,b);break
            except RuntimeError as e:error=e
        else:raise error

for layer in [p.F_Cu,p.B_Cu]:
    z=p.ZONE(board);z.SetLayer(layer);z.SetNetCode(at('J1.2').GetNetCode());z.SetLocalClearance(p.FromMM(.25));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.5));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.2))
    poly=z.Outline();poly.NewOutline()
    for x,y in [(50.7,50.7),(149.3,50.7),(149.3,139.3),(50.7,139.3)]:poly.Append(p.FromMM(x),p.FromMM(y))
    board.Add(z)
board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(FILE),board)
print(f'Saved {len(done)} connections. Run KiCad DRC; do not fabricate on router status alone.',flush=True)
