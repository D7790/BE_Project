"""Compare native schematic netlist, PCB, manifest, and critical pin mappings.
Run after fresh KiCad ERC/DRC and XML netlist export, with KiCad's Python.
"""
from pathlib import Path
import hashlib, json, math, xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'design.json').read_text())
parts={c['ref']:c for c in data['parts']}
board=p.LoadBoard(str(ROOT/'wattsense-main.kicad_pcb'))
fps={f.GetReference():f for f in board.GetFootprints()}
assert set(parts)==set(fps),'Footprint inventory differs from design manifest'
expected={(ref,n):net for ref,c in parts.items() for n,net in c['nets'].items()}
actual={(f.GetReference(),a.GetNumber()):a.GetNetname().lstrip('/') for f in fps.values() for a in f.Pads() if a.GetNumber()}
assert actual==expected,{'missing_or_changed':{str(k):(v,actual.get(k)) for k,v in expected.items() if actual.get(k)!=v}}
xml=ET.parse(ROOT/'reports'/'schematic.net.xml')
schematic={}
for net in xml.findall('./nets/net'):
    for node in net.findall('node'):
        ref=node.get('ref')
        if not ref.startswith('#'):schematic[ref,node.get('pin')]=net.get('name').lstrip('/')
assert schematic==expected,'Native schematic netlist differs from PCB/manifest'

# Independent manufacturer/architecture assertions (not derived from manifest).
for ref,addr,plus,minus in [('U1',('GND','GND'),'BAT_P','SYS_P'),('U2',('GND','3V3'),'SYS_P','BUCK_P'),('U3',('3V3','GND'),'CHG_P','SYS_P')]:
    pinmap={'1':addr[0],'2':addr[1],'3':'SDA','4':'SCL','5':'3V3','6':'GND','7':minus,'8':plus}
    for pin,net in pinmap.items():assert actual[ref,pin]==net,(ref,pin,net)
    assert fps[ref].GetFPID().GetLibItemName()=='SOIC-8_3.9x4.9mm_P1.27mm'
    assert parts[ref]['mpn']=='INA219AID'
critical={
 'Q1':{'1':'FAN_GATE','2':'GND','3':'FAN_RETURN'},
 'D1':{'1':'FAN_P','2':'FAN_RETURN'},'D2':{'1':'SYS_P','2':'GND'},
 'R1':{'1':'BAT_P','2':'SYS_P'},'R2':{'1':'SYS_P','2':'BUCK_P'},'R3':{'1':'CHG_P','2':'SYS_P'},
 'F1':{'1':'5V_IN','2':'5V'},'F2':{'1':'5V','2':'LAMP_P'},'F3':{'1':'5V','2':'FAN_P'},
 'J1':{'1':'BAT_P','2':'GND'},'J2':{'1':'CHG_P','2':'GND'},'J3':{'1':'BUCK_P','2':'GND'},
 'J4':{'1':'5V_IN','2':'GND'},'J5':{'1':'LAMP_P','2':'GND'},'J6':{'1':'FAN_P','2':'FAN_RETURN'},
 'J7':dict(zip(map(str,range(1,9)),['3V3','GND','SDA','SCL','FAN_EN','TEMP_DQ','BTN_LOAD','BTN_FULL'])),
 'JP1':{'1':'5V','2':'ESP_5V'},'J11':{'1':'ESP_5V','2':'GND'},
}
for ref,pins in critical.items():
    for pin,net in pins.items():assert actual[ref,pin]==net,(ref,pin,net)
for ref,part in [('F1','0466002.NR'),('F2','0466001.NR'),('F3','0466001.NR')]:
    assert parts[ref]['mpn']==part
    assert '1206' in str(fps[ref].GetFPID().GetLibItemName())

erc=json.loads((ROOT/'reports'/'erc.json').read_text())
erc_items=[v for sheet in erc.get('sheets',[]) for v in sheet.get('violations',[])]
assert not erc_items,erc_items
drc=json.loads((ROOT/'reports'/'drc.json').read_text())
for key in ['violations','unconnected_items','schematic_parity']:
    assert key in drc and not drc[key],f'DRC has outstanding {key}: {len(drc.get(key,[]))}'
assert board.GetCopperLayerCount()==2
outline=board.GetBoardEdgesBoundingBox()
assert abs(p.ToMM(outline.GetWidth())-100)<.1
assert abs(p.ToMM(outline.GetHeight())-90)<.1
tracks=list(board.GetTracks())
vias=[t for t in tracks if isinstance(t,p.PCB_VIA)]
assert len(tracks)>100 and len(board.Zones())==2
assert all(abs(p.ToMM(v.GetDrillValue())-.35)<1e-5 for v in vias)
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['wattsense-main.kicad_sch','wattsense-main.kicad_pcb','wattsense-main.kicad_pro','BOM.csv']}
result={'status':'PASS','pcb_components':len(parts),'electrical_pin_assignments':len(actual),'nets':len(set(actual.values())),'copper_layers':2,'board_mm':[100,90],'tracks_and_vias':len(tracks),'vias':len(vias),'erc_violations':0,'drc_violations':0,'unconnected_items':0,'schematic_parity_issues':0,'critical_pin_mapping_checks':'PASS','hardware_validation':'NOT PERFORMED','sha256':hashes}
(ROOT/'reports'/'connectivity-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
