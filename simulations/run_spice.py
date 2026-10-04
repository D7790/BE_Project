"""Executable reduced-circuit SPICE checks, not a complete component simulation."""
from pathlib import Path
import csv, hashlib, json, math
from ngspice_shared import Spice

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; CIRCUITS=ROOT/'circuits'
OUT.mkdir(exist_ok=True); CIRCUITS.mkdir(exist_ok=True)
PCB=ROOT.parent/'hardware/pcb/wattsense-main-revB-4layer'
audit=json.loads((PCB/'reports/connectivity-audit.json').read_text())
assert audit['status']=='PASS' and audit['revision']=='B'
for name,digest in audit['sha256'].items():
    assert hashlib.sha256((PCB/name).read_bytes()).hexdigest()==digest, f'Recheck changed CAD: {name}'
parts={p['ref']:p for p in json.loads((PCB/'design.json').read_text())['parts']}
for ref,value in {'R1':'0.1R 1% 1W','R2':'0.1R 1% 1W','R3':'0.1R 1% 1W','R4':'2.2k','R5':'2.2k','R7':'330R','R8':'47k'}.items():
    assert parts[ref]['value']==value, f'Update reduced model for changed {ref}'
for ref,nets in {'R1':{'1':'BAT_P','2':'SYS_P'},'R2':{'1':'SYS_P','2':'BUCK_P'},'R3':{'1':'CHG_P','2':'SYS_P'},'R7':{'1':'FAN_EN','2':'FAN_GATE'},'R8':{'1':'FAN_GATE','2':'GND'},'D1':{'1':'FAN_P','2':'FAN_RETURN'},'Q1':{'1':'FAN_GATE','2':'GND','3':'FAN_RETURN'}}.items():
    assert parts[ref]['nets']==nets, f'Update reduced topology for changed {ref}'
spice=Spice(); cases=[]
generated=[]

def run(name,netlist,vectors):
    (CIRCUITS/(name+'.cir')).write_text(netlist.strip()+'\n')
    generated.append(CIRCUITS/(name+'.cir'))
    values=spice.run(netlist,vectors)
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.writer(f); w.writerow(values); w.writerows(zip(*values.values()))
    (OUT/(name+'.log')).write_text('\n'.join(spice.log))
    return values

dc=run('three_shunt_dc','''Wattsense R1 R2 R3 signed current sweep
* Exact schematic shunt topology; fixed ideal battery and ideal branch currents.
Vbat BAT_P 0 12.8
R1 BAT_P SYS_P 0.1
R2 SYS_P BUCK_P 0.1
R3 CHG_P SYS_P 0.1
Iload BUCK_P 0 0
Ichg 0 CHG_P 0
.dc Iload 0 2 0.25 Ichg 0 2 1
.end
''',['v(bat_p)','v(sys_p)','v(buck_p)','v(chg_p)','i(vbat)'])
max_error=0; max_power=0
for i in range(len(dc['v(bat_p)'])):
    load=(i%9)*.25; charge=(i//9)*1.0; battery=load-charge
    drops=[dc['v(bat_p)'][i]-dc['v(sys_p)'][i],dc['v(sys_p)'][i]-dc['v(buck_p)'][i],dc['v(chg_p)'][i]-dc['v(sys_p)'][i]]
    expected=[battery*.1,load*.1,charge*.1]
    max_error=max(max_error,*(abs(a-b) for a,b in zip(drops,expected)),abs(dc['i(vbat)'][i]+battery))
    max_power=max(max_power,*(d*d/.1 for d in drops))
assert max_error<1e-8 and max_power<.400001
cases.append({'case':'Three-shunt signed DC sweep','status':'PASS','points':len(dc['v(bat_p)']),'maximum_shunt_dissipation_W':max_power,'max_numeric_error':max_error,'battery_to_load_drop_at_2A_V':.4})

fan=run('fan_switch_transient','''Wattsense illustrative fan switching / flyback
* Q1 replaced with voltage-controlled resistance: NOT vendor AO3400A model.
* 48 milliohm on-resistance is a datasheet reference at room temperature.
* 1nF gate capacitance, 1mH load inductance and diode model are assumptions.
V5 FAN_P 0 5
Vgpio GPIO 0 PULSE(0 3.3 2m 10n 10n 3m 10m)
R7 GPIO FAN_GATE 330
R8 FAN_GATE 0 47k
Cgate FAN_GATE 0 1n
Rfan FAN_P COIL 8.333333
Lfan COIL FAN_RETURN 1m
Smos FAN_RETURN 0 FAN_GATE 0 SWQ
.model SWQ SW(Ron=0.048 Roff=1e9 Vt=1.65 Vh=0.02)
D1 FAN_RETURN FAN_P DFLY
.model DFLY D(Is=1u N=1.05 Rs=0.05 Cjo=60p Bv=40)
.tran 1u 8m 0 1u
.end
''',['time','v(fan_gate)','v(fan_return)','i(lfan)'])
gate=max(fan['v(fan_gate)']); peak=max(fan['v(fan_return)']); current=max(fan['i(lfan)'])
assert 3.27<gate<3.29 and 5<peak<6 and .58<current<.61
assert abs(fan['i(lfan)'][-1])<1e-5
cases.append({'case':'Behavioural fan switch and generic flyback transient','status':'PASS','gate_high_V':gate,'peak_drain_V':peak,'steady_fan_A':current,'switch_conduction_W_at_48mOhm':current*current*.048,'scope':'Not a vendor MOSFET/BLDC fan model; no parasitic overshoot or junction-temperature prediction.'})

reset=run('gate_high_impedance_reset','''Wattsense gate discharge when controller goes high impedance
* External 47k pulldown and assumed 1nF gate capacitance.
R8 FAN_GATE 0 47k
Cgate FAN_GATE 0 1n IC=3.277
.tran .1u 1m 0 .1u UIC
.end
''',['time','v(fan_gate)'])
off=next(t for t,v in zip(reset['time'],reset['v(fan_gate)']) if v<.5)
assert off<.00011
cases.append({'case':'Gate pulldown with GPIO high impedance','status':'PASS','time_below_0_5V_us':off*1e6,'assumed_gate_capacitance_nF':1})

def crossing(ts,vs,level,start=1e-6):
    for i in range(1,len(ts)):
        if ts[i]>start and vs[i-1]<level<=vs[i]:
            return ts[i-1]+(level-vs[i-1])*(ts[i]-ts[i-1])/(vs[i]-vs[i-1])
    raise AssertionError('No crossing')
for resistor,cap in [(4700,100),(4700,200),(4700,400),(2200,100),(2200,200),(2200,400)]:
    r=run(f'i2c_rise_{resistor}ohm_{cap}pF',f'''Wattsense pullup bus capacitance envelope
V3 VCC 0 3.3
Rpull VCC SDA {resistor}
Cbus SDA 0 {cap}p
Vctrl CTRL 0 PULSE(3.3 0 1u 1n 1n 9u 20u)
Ssink SDA 0 CTRL 0 SOPEN
.model SOPEN SW(Ron=20 Roff=1e12 Vt=1.65 Vh=0.02)
.tran 2n 10u 0 2n
.end
''',['time','v(sda)'])
    rise=crossing(r['time'],r['v(sda)'],.7*3.3)-crossing(r['time'],r['v(sda)'],.3*3.3)
    assert abs(rise/(.84729786*resistor*cap*1e-12)-1)<.002
    if resistor==2200: assert rise<1e-6
    cases.append({'case':f'I2C rise with {resistor} ohm at {cap} pF','status':'PASS' if rise<=1e-6 else 'OUTSIDE_ENVELOPE','rise_30_70_ns':rise*1e9,'standard_mode_limit_ns':1000,'ideal_sink_current_mA':3300/resistor})

result={'engine':'KiCad bundled ngspice shared DLL','version_log':spice.version_log,'hardware_tested':False,'cases':cases,'checked_cad_sha256':audit['sha256'],'netlist_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in generated},'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'ngspice_shared.py']}}
(OUT/'spice-summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
