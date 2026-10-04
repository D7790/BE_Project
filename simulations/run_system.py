"""Accelerated deterministic plant runs. All output is simulated, never measured."""
from pathlib import Path
import csv, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from wattsense.model import Controller,Config
OUT=ROOT/'simulations/results'; OUT.mkdir(exist_ok=True)

def discharge(name,automatic,capacity=6,efficiency=.90,essential=3,optional=3,initial_soc=68):
    c=Controller(Config(capacity_ah=capacity)); c.synchronize(initial_soc); c.optional_on=True
    truth=initial_soc; rows=[]; shed=None; previous=None
    # Ideal constant 12.8 V battery; 0.8 W controller consumption at converter output.
    # Terminate at 20% *true* charge reserve, not at an arbitrary hardware cutoff.
    for sec in range(1,24*3600+1):
        load=(essential+(optional if c.optional_on else 0)+.8)/efficiency
        current=load/12.8
        truth-=100*current/(3600*capacity)
        r=c.update(1,12.8,current,load,28,automatic=automatic)
        if automatic and not c.optional_on and shed is None: shed=sec
        if sec%60==0 or c.state!=previous or truth<=20:
            rows.append([sec,truth,c.soc_pct,load,current,c.optional_on,c.state])
        previous=c.state
        assert abs(truth-c.soc_pct)<1e-9
        if truth<=20: break
    else: raise AssertionError('Model did not reach reserve')
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['time_s','true_soc_pct','estimated_soc_pct','load_input_W','battery_A','optional_on','state']); w.writerows(rows)
    return {'name':name,'runtime_to_true_reserve_h':sec/3600,'shed_time_h':None if shed is None else shed/3600,
            'capacity_Ah':capacity,'converter_efficiency':efficiency,'model':'constant 12.8 V, exact capacity, no solar, no ageing or noise'}

baseline=discharge('runtime_baseline',False)
priority=discharge('runtime_priority',True)
analytical=.48*6*12.8/((3+3+.8)/.9)
assert abs(baseline['runtime_to_true_reserve_h']-analytical)<1/3600
assert priority['runtime_to_true_reserve_h']>baseline['runtime_to_true_reserve_h']
sweeps=[]
for cap in [4,6,8]:
    for eff in [.80,.90,.95]:
        base=discharge(f'sweep_{cap}Ah_{int(eff*100)}eff_baseline',False,cap,eff)
        controlled=discharge(f'sweep_{cap}Ah_{int(eff*100)}eff_priority',True,cap,eff)
        assert controlled['runtime_to_true_reserve_h']>base['runtime_to_true_reserve_h']
        sweeps.append({'capacity_Ah':cap,'efficiency':eff,'baseline_h':base['runtime_to_true_reserve_h'],'priority_h':controlled['runtime_to_true_reserve_h']})

faults=[]
for name,fields in [('sensor_disconnect',{'sensor_ok':False}),('temperature',{'temperature_c':46}),
                    ('low_voltage',{'voltage_v':11.5}),('high_voltage',{'voltage_v':14.8}),
                    ('current_overrange',{'battery_current_a':2.1}),('integration_gap',{'dt_s':2.1}),
                    ('nan_temperature',{'temperature_c':float('nan')})]:
    c=Controller(); c.synchronize(80); c.optional_on=True
    args=dict(dt_s=.1,voltage_v=12.8,battery_current_a=.5,load_w=6.4,temperature_c=28); args.update(fields)
    r=c.update(**args); assert not r['optional_on']
    faults.append({'case':name,'state':r['state'],'optional_on':r['optional_on'],'charge_reference_valid':r['estimate_valid']})

c=Controller(); c.synchronize(60)
for _ in range(3600): r=c.update(1,12.8,-.5,4,28)
assert abs(c.soc_pct-(60+100*.5*.98/6))<1e-8
assert r['runtime_h'] is None and r['runtime_no_solar_h']>0

# Independent estimation error experiment: true capacity 4.8 Ah, configured 6 Ah.
# This explicitly demonstrates a limitation instead of pretending exact knowledge.
true_soc=80.; estimated=Controller(); estimated.synchronize(80)
for _ in range(4*3600):
    true_soc-=100*.5/(3600*4.8)
    estimated.update(1,12.8,.52,6.4,28,requested=False)
error=estimated.soc_pct-true_soc
assert 6<error<7.5
result={'provenance':'SIMULATION ONLY - not experimental results','baseline':baseline,'priority':priority,
        'runtime_extension_pct':100*(priority['runtime_to_true_reserve_h']/baseline['runtime_to_true_reserve_h']-1),
        'sweep_pairs':sweeps,'fault_cases':faults,'one_hour_charge_final_soc_pct':c.soc_pct,
        'capacity_and_offset_error':{'true_capacity_Ah':4.8,'configured_capacity_Ah':6,'true_discharge_A':.5,'measured_discharge_A':.52,'hours':4,'true_soc_pct':true_soc,'estimated_soc_pct':estimated.soc_pct,'error_percentage_points':error},
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'wattsense/model.py',Path(__file__)]}}
(OUT/'system-summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
