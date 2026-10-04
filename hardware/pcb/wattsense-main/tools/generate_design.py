"""Reproducible Wattsense Rev A engineering prototype. Run with KiCad Python.

The generated native KiCad sources remain editable without this script.
This generator overwrites only its named project files; never run over hand edits.
"""
from pathlib import Path
import copy, csv, json, math, re, uuid
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
KICAD = Path(r'C:\Program Files\KiCad\10.0\share\kicad')
NAME = 'wattsense-main'
NS = uuid.UUID('5e3591b0-702c-41bb-9fb6-676631b527cd')
uid = lambda s: str(uuid.uuid5(NS, s))
q = lambda s: json.dumps(str(s))

class Atom(str): pass
def parse(s):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', s)
    stack, root = [], None
    for t in tokens:
        if t == '(':
            a=[]
            if stack: stack[-1].append(a)
            else: root=a
            stack.append(a)
        elif t == ')': stack.pop()
        else: stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
    return root
def dump(x):
    if isinstance(x, list): return '('+' '.join(map(dump,x))+')'
    return str(x) if isinstance(x,Atom) else q(x)
def child(a,k): return next((x for x in a if isinstance(x,list) and x and x[0]==k),None)
def children(a,k): return [x for x in a if isinstance(x,list) and x and x[0]==k]

libs={}
def symbol(lib, name):
    if lib not in libs:
        libs[lib]={x[1]:x for x in children(parse((KICAD/'symbols'/f'{lib}.kicad_sym').read_text()),'symbol')}
    s=copy.deepcopy(libs[lib][name])
    ext=child(s,'extends')
    if ext:
        base=symbol(lib,ext[1])
        props={x[1] for x in children(s,'property')}
        s.remove(ext)
        for item in base[2:]:
            if isinstance(item,list) and item[0]=='property' and item[1] in props: continue
            if isinstance(item,list) and item[0]=='symbol': item[1]=item[1].replace(base[1]+'_',name+'_',1)
            if item not in s: s.append(item)
    return s

PARTS=[]
def add(ref,value,lib,sym,foot,nets,xy,sch,rot=0,mpn='',note=''):
    PARTS.append(dict(ref=ref,value=value,lib=lib,sym=sym,foot=foot,nets={str(k):v for k,v in nets.items()},xy=xy,sch=sch,rot=rot,mpn=mpn,note=note,uuid=uid(ref)))
TERM='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
R0805='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C0805='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
SOIC='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
SHUNT='Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder'
HDR=lambda n:f'Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical'
for ref,val,nets,xy,sch in [
 ('J1','BATTERY_AFTER_FUSE',{1:'BAT_P',2:'GND'},(61,59),(30.48,38.1)),
 ('J2','CHARGER_BAT_PORT',{1:'CHG_P',2:'GND'},(96,59),(157.48,38.1)),
 ('J3','TO_BUCK_INPUT',{1:'BUCK_P',2:'GND'},(128,59),(287.02,38.1)),
 ('J4','FROM_BUCK_5V',{1:'5V_IN',2:'GND'},(61,128),(30.48,187.96)),
 ('J5','ESSENTIAL_LAMP',{1:'LAMP_P',2:'GND'},(95,128),(121.92,187.96)),
 ('J6','OPTIONAL_FAN',{1:'FAN_P',2:'FAN_RETURN'},(128,128),(218.44,187.96)),
]: add(ref,val,'Connector_Generic','Conn_01x02',TERM,nets,xy,sch,mpn='Phoenix Contact 1715721',note='MKDS 1,5/2-5,08; 5.08 mm, 2-way; + is pin 1. Check exact purchased connector dimensions.')
for i,x,schx,plus,minus in [(1,69,66.04,'BAT_P','SYS_P'),(2,130,320.04,'SYS_P','BUCK_P'),(3,99,193.04,'CHG_P','SYS_P')]:
    add(f'R{i}','0.1R 1% 1W','Device','R',SHUNT,{1:plus,2:minus},(x,73),(schx,38.1),mpn='WSL2512R1000FEA',note='Vishay 2512 current shunt; use separate sense tracks from its pads.')
    add(f'U{i}','INA219AID','Sensor_Energy','INA219AxD',SOIC,{1:'3V3' if i==3 else 'GND',2:'3V3' if i==2 else 'GND',3:'SDA',4:'SCL',5:'3V3',6:'GND',7:minus,8:plus},(x-1,84),(schx,81.28),rot=90,mpn='INA219AID',note=f'SOIC-8, address { {1:"0x40 battery",2:"0x41 load",3:"0x44 charger"}[i] }. Do not substitute DCN pinout.')
    add(f'C{i}','100n 16V X7R','Device','C',C0805,{1:'3V3',2:'GND'},(x+5,81.5),(schx+35.56,81.28),mpn='GRM21BR71C104KA01L')
    add(f'C{i+7}','10n 50V X7R','Device','C',C0805,{1:plus,2:minus},(x-2.27,77.5),(schx-38.1,81.28),mpn='GRM21BR71H103KA01L',note='Differential input capacitor; no shared high-current sense routing.')

add('J7','ESP32_SIGNALS','Connector_Generic','Conn_01x08',HDR(8),dict(enumerate(['3V3','GND','SDA','SCL','FAN_EN','TEMP_DQ','BTN_LOAD','BTN_FULL'],1)),(57,92),(38.1,134.62),note='Cable to classic ESP32; pin map in assembly guide. 3V3 is input from ESP32.')
add('J8','DS18B20','Connector_Generic','Conn_01x03',HDR(3),{1:'3V3',2:'TEMP_DQ',3:'GND'},(70,110),(129.54,129.54),note='Powered 3-wire temperature probe; verify probe wire mapping.')
add('J9','LOAD_BUTTON','Connector_Generic','Conn_01x02',HDR(2),{1:'BTN_LOAD',2:'GND'},(84,110),(195.58,124.46),note='External normally-open momentary button.')
add('J10','FULL_CONFIRM','Connector_Generic','Conn_01x02',HDR(2),{1:'BTN_FULL',2:'GND'},(97,110),(195.58,147.32),note='External normally-open button; hold 5 s only after verified full charge.')
for ref,val,nets,xy,sch,mpn in [
 ('R4','4.7k',{1:'3V3',2:'SDA'},(77,97),(68.58,129.54),'RC0805FR-074K7L'),
 ('R5','4.7k',{1:'3V3',2:'SCL'},(85,97),(91.44,129.54),'RC0805FR-074K7L'),
 ('R6','4.7k',{1:'3V3',2:'TEMP_DQ'},(72,104),(160.02,129.54),'RC0805FR-074K7L'),
 ('R7','330R',{1:'FAN_EN',2:'FAN_GATE'},(114,105),(254,223.52),'RC0805FR-07330RL'),
 ('R8','47k',{1:'FAN_GATE',2:'GND'},(121,113),(284.48,243.84),'RC0805FR-0747KL'),
 ('R9','10k',{1:'3V3',2:'BTN_LOAD'},(87,104),(228.6,124.46),'RC0805FR-0710KL'),
 ('R10','10k',{1:'3V3',2:'BTN_FULL'},(97,104),(228.6,147.32),'RC0805FR-0710KL'),
]: add(ref,val,'Device','R',R0805,nets,xy,sch,mpn=mpn)
for ref,val,nets,xy,sch in [
 ('C4','1u 16V X7R',{1:'3V3',2:'GND'},(63,88),(68.58,154.94)),
 ('C5','100n 16V X7R',{1:'5V',2:'GND'},(85,119),(66.04,218.44)),
 ('C6','100n 16V X7R',{1:'BTN_LOAD',2:'GND'},(89,113),(254,124.46)),
 ('C7','100n 16V X7R',{1:'BTN_FULL',2:'GND'},(102,113),(254,147.32)),
]: add(ref,val,'Device','C',C0805,nets,xy,sch,note='0805 ceramic; specified voltage is minimum.')
add('C11','47u 25V','Device','C_Polarized','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',{1:'5V',2:'GND'},(78,122),(91.44,218.44),mpn='Panasonic EEU-FR1E470',note='Observe polarity; verify 5 mm diameter / 2 mm lead pitch.')
add('Q1','AO3400A','Transistor_FET','AO3400A','Package_TO_SOT_SMD:SOT-23',{1:'FAN_GATE',2:'GND',3:'FAN_RETURN'},(126,109),(312.42,223.52),mpn='AO3400A',note='Low-side switch, 3.3 V gate; pin 1 G, 2 S, 3 D.')
add('D1','SS14','Device','D_Schottky','Diode_SMD:D_SMA',{1:'FAN_P',2:'FAN_RETURN'},(136,116),(254,187.96),rot=90,mpn='SS14-E3/61T',note='Flyback: cathode stripe to fan positive.')
add('D2','SMBJ15A','Device','D_Zener','Diode_SMD:D_SMB',{1:'SYS_P',2:'GND'},(114,65),(228.6,38.1),rot=90,mpn='SMBJ15A-E3/52',note='Unidirectional TVS, cathode to SYS_P. Does not provide reverse-polarity protection.')
for ref,val,nets,xy,sch,mpn in [
 ('F1','2A 63V FAST',{1:'5V_IN',2:'5V'},(65,119),(66.04,187.96),'0466002.NR'),
 ('F2','1A 63V FAST',{1:'5V',2:'LAMP_P'},(96,119),(157.48,187.96),'0466001.NR'),
 ('F3','1A 63V FAST',{1:'5V',2:'FAN_P'},(127,119),(193.04,210.82),'0466001.NR'),
]: add(ref,val,'Device','Fuse','Fuse:Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder',nets,xy,sch,rot=90 if ref=='F1' else 270,mpn=mpn,note='Littelfuse 466 series 1206; allow 25% continuous-current derating. Validate startup pulse/time-current before final assembly.')
add('JP1','REMOVE_FOR_USB','Connector_Generic','Conn_01x02',HDR(2),{1:'5V',2:'ESP_5V'},(109,125),(353.06,187.96),note='Normally OPEN. Fit shunt only for battery-powered ESP32 with USB VBUS absent.')
add('J11','ESP32_5V_OPTION','Connector_Generic','Conn_01x02',HDR(2),{1:'ESP_5V',2:'GND'},(116,130),(388.62,187.96),note='To documented ESP32 5V input only. JP1 open for ordinary USB.')
for i,net,xy,sch in [(1,'GND',(108,94),(292.1,132.08)),(2,'3V3',(112,94),(312.42,132.08)),(3,'SYS_P',(116,94),(332.74,132.08)),(4,'FAN_GATE',(120,94),(353.06,132.08))]:
    add(f'TP{i}',net,'Connector','TestPoint','TestPoint:TestPoint_Pad_D2.0mm',{1:net},xy,sch)
for i,xy in enumerate([(54,54),(146,54),(54,136),(146,136)],1):
    add(f'H{i}','M3_NYLON','Mechanical','MountingHole','MountingHole:MountingHole_3.2mm_M3',{},xy,(320.04+(i-1)*22.86,157.48),note='Use insulating M3 standoffs; no electrical connection.')

def make_schematic():
    syms={}
    for c in PARTS: syms[c['sym']]=symbol(c['lib'],c['sym'])
    syms['PWR_FLAG']=symbol('power','PWR_FLAG')
    library='(kicad_symbol_lib (version 20250114) (generator "wattsense")\n'+'\n'.join(dump(s) for s in syms.values())+'\n)'
    (ROOT/'Wattsense.kicad_sym').write_text(library)
    (ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Wattsense") (type "KiCad") (uri "${KIPRJMOD}/Wattsense.kicad_sym") (options "") (descr "Project-local symbols copied from KiCad 10; manufacturer mappings checked")))')
    embedded=[]
    for s in syms.values():
        s=copy.deepcopy(s); s[1]='Wattsense:'+s[1]; embedded.append(dump(s))
    out=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A3")',
         '(title_block (title "Wattsense main controller") (date "2026-09-27") (rev "A") (company "Final-year electronics project") (comment 1 "Engineering prototype - hardware validation pending") (comment 2 "Protected 4S LiFePO4 / 14.6 V / 2 A"))',
         '(lib_symbols '+'\n'.join(embedded)+')']
    def text(t,x,y,size=1.27):
        out.append(f'(text {q(t)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid "{uid(t)}"))')
    def label(net,x,y,angle=0):
        justify='right' if angle==180 else 'left'
        out.append(f'(label {q(net)} (at {x:.4f} {y:.4f} 0) (effects (font (size 1.016 1.016)) (justify {justify} bottom)) (uuid "{uid(net+str(x)+str(y))}"))')
    for c in PARTS:
        x,y=c['sch']; ref=c['ref']; sym=syms[c['sym']]
        pins=[pin for unit in children(sym,'symbol') for pin in children(unit,'pin')]
        rx,ry,vx,vy,justify=x+3.81,y-1.27,x+3.81,y+1.27,'(justify left)'
        if ref.startswith('U'): rx,ry,vx,vy,justify=x-6.35,y-8.89,x+3.81,y-11.43,'(justify left)'
        elif ref.startswith('D'): rx,ry,vx,vy,justify=x,y-5.08,x,y-2.54,''
        elif ref.startswith('Q'): rx,ry,vx,vy,justify=x+7.62,y-5.08,x+7.62,y-2.54,'(justify left)'
        elif ref.startswith('TP') or ref.startswith('H'): rx,ry,vx,vy,justify=x,y-6.35,x,y-3.81,''
        props=f'(property "Reference" {q(ref)} (at {rx} {ry} 0) (effects (font (size 1.27 1.27)) {justify})) (property "Value" {q(c["value"])} (at {vx} {vy} 0) (effects (font (size 1.016 1.016)) {justify})) (property "Footprint" {q(c["foot"])} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))'
        instances=f'(instances (project "{NAME}" (path "/{uid("root")}" (reference "{ref}") (unit 1))))'
        out.append(f'(symbol (lib_id "Wattsense:{c["sym"]}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{c["uuid"]}") {props} {instances})')
        for pin in pins:
            num=child(pin,'number')[1]; at=child(pin,'at'); px,py=x+float(at[1]),y-float(at[2]); angle=float(at[3]); rad=math.radians(angle)
            ex,ey=px-2.54*math.cos(rad),py+2.54*math.sin(rad)
            out.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {ex:.4f} {ey:.4f})) (stroke (width 0) (type default)) (uuid "{uid(ref+num+"wire")}"))')
            label(c['nets'][num],ex,ey,180 if angle==0 else 0)
    for i,(net,x,y) in enumerate([('3V3',375.92,127),('GND',398.78,127)],1):
        ref=f'#FLG0{i:02d}'
        out.append(f'(symbol (lib_id "Wattsense:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref)}") (property "Reference" "{ref}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "PWR_FLAG" (at {x} {y-4} 0) (effects (font (size 1.016 1.016)))) (instances (project "{NAME}" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
        label(net,x,y)
    text('01 / PROTECTED DC POWER PATHS',12.7,15.24,2)
    text('BAT -> R1 -> SYS -> R2 -> BUCK. Charger -> R3 -> SYS. All returns use protected pack P-.',12.7,21.59)
    text('J1 requires a DC fuse near the battery AND a manual disconnect. J2: one matched charger only, <= 1 A; never connect a raw solar panel.',12.7,55.88)
    text('02 / THREE 3.3 V CURRENT MONITORS - SOIC PINOUT',12.7,63.5,2)
    text('U1 0x40 battery / U2 0x41 buck input / U3 0x44 charger output. R1-R3 0.1 ohm, 1 W. Separate sense takeoffs at shunt pads.',12.7,103)
    text('03 / ESP32 SIGNAL HARNESS, TEMPERATURE AND LOCAL BUTTONS',12.7,113.03,2)
    text('J7 pins: 1=3V3, 2=GND, 3=GPIO21, 4=GPIO22, 5=GPIO25, 6=GPIO4, 7=GPIO27, 8=GPIO26. Keep cable <= 100 mm.',12.7,170.18)
    text('04 / FUSED 5 V LOADS AND DEFAULT-OFF FAN SWITCH',12.7,177.8,2)
    text('Q1 low-side switches a power-only fan. No secondary fan ground/data connection.',12.7,241.3)
    text('JP1 OPEN for USB. Fit only with USB VBUS absent. J11 is optional ESP32 power, not 3.3 V.',12.7,248.92)
    text('TARGET: 2 A battery path. 5 V continuous <= 1.5 A total; lamp and fan <= 0.6 A each. Include ESP32 consumption.',12.7,261.62)
    text('Prototype fabrication package: ERC/DRC are design checks; calibration, thermal and fault tests remain required.',12.7,269.24)
    out.append('(embedded_fonts no))')
    (ROOT/f'{NAME}.kicad_sch').write_text('\n'.join(out))

def make_board():
    b=p.BOARD(); b.SetCopperLayerCount(2)
    ds=b.GetDesignSettings(); ds.SetBoardThickness(p.FromMM(1.6)); ds.m_MinClearance=p.FromMM(.2); ds.m_TrackMinWidth=p.FromMM(.2); ds.m_CopperEdgeClearance=p.FromMM(.5); ds.m_HoleClearance=p.FromMM(.25); ds.m_HoleToHoleMin=p.FromMM(.25)
    netnames=sorted({v for c in PARTS for v in c['nets'].values()})
    nets={}
    for i,name in enumerate(netnames,1):
        net=p.NETINFO_ITEM(b,'/'+name,i); b.Add(net); nets[name]=net
    fps={}
    for c in PARTS:
        lib,name=c['foot'].split(':'); f=p.FootprintLoad(str(KICAD/'footprints'/f'{lib}.pretty'),name)
        if not f: raise RuntimeError(c['foot'])
        f.SetFPID(p.LIB_ID(lib,name))
        f.SetExcludedFromBOM(False)
        f.SetReference(c['ref']); f.SetValue(c['value']); f.SetPosition(p.VECTOR2I(*[p.FromMM(z) for z in c['xy']]))
        f.SetOrientationDegrees(c['rot']); f.SetPath(p.KIID_PATH(f'/{uid("root")}/{c["uuid"]}'))
        f.SetSheetname(''); f.SetSheetfile(f'{NAME}.kicad_sch')
        f.Value().SetVisible(False)
        f.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.85),p.FromMM(.85))); f.Reference().SetTextThickness(p.FromMM(.13))
        if c['ref'] in ['H1','H2']: f.Reference().SetPosition(p.VECTOR2I(p.FromMM(c['xy'][0]),p.FromMM(58.5)))
        if c['ref']=='J2': f.Reference().SetPosition(p.VECTOR2I(p.FromMM(91),p.FromMM(58)))
        for pad in f.Pads():
            n=pad.GetNumber()
            if n in c['nets']: pad.SetNet(nets[c['nets'][n]])
        b.Add(f); fps[c['ref']]=f
    for start,end in [((50,50),(150,50)),((150,50),(150,140)),((150,140),(50,140)),((50,140),(50,50))]:
        line=p.PCB_SHAPE(); line.SetShape(p.SHAPE_T_SEGMENT); line.SetStart(p.VECTOR2I(*map(p.FromMM,start))); line.SetEnd(p.VECTOR2I(*map(p.FromMM,end))); line.SetLayer(p.Edge_Cuts); line.SetWidth(p.FromMM(.05)); b.Add(line)
    def txt(t,x,y,size=.9,layer=p.F_SilkS):
        a=p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y))); a.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size))); a.SetTextThickness(p.FromMM(.14)); a.SetLayer(layer); b.Add(a)
    txt('WATTSENSE  /  REV A',99,51.8,1.2)
    txt('ENGINEERING PROTOTYPE',97,136.5,.9)
    txt('4S LiFePO4  |  14.6V  |  2A MAX',98,139,.8)
    for t,x,y in [('BAT +  -',63.5,66),('CHG +  -',98.5,66),('BUCK +  -',130.5,66),('5V IN + -',63.5,135),('LAMP + -',97.5,135),('FAN + SW-',130.5,135),('0x40',69,89),('0x44',99,89),('0x41',130,89),('ESP SIGNALS',60,115),('TEMP',74.5,110),('LOAD',84,116),('FULL',97,116),('USB: JP1 OPEN',110,121)]: txt(t,x,y,.8)
    p.SaveBoard(str(ROOT/f'{NAME}.kicad_pcb'),b)
    # Design data is a reviewable, independent manifest used for connectivity audit.
    (ROOT/'design.json').write_text(json.dumps({'revision':'A','root_uuid':uid('root'),'parts':PARTS},indent=2))
    with (ROOT/'BOM.csv').open('w',newline='') as f:
        writer=csv.writer(f); writer.writerow(['Reference','Value','Manufacturer_part','Footprint','Notes'])
        for c in PARTS: writer.writerow([c['ref'],c['value'],c['mpn'],c['foot'],c['note']])
    # Local project preserves explicit manufacturable defaults; no violations hidden.
    project={'meta':{'filename':NAME+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.2,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.5,'min_hole_clearance':.25,'min_hole_to_hole':.25,'min_silk_clearance':.15},'rule_severities':{},'drc_exclusions':[]}},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.7,'via_drill':.35,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],'meta':{'version':3}},'schematic':{'drawing':{'default_line_thickness':6.0,'default_text_size':50.0},'erc':{'erc_exclusions':[]}}}
    (ROOT/f'{NAME}.kicad_pro').write_text(json.dumps(project,indent=2))
    print(f'Created {len(PARTS)} components / {len(nets)} nets; board 100 x 90 mm. Routing is a separate step.')

if __name__=='__main__':
    make_schematic(); make_board()
