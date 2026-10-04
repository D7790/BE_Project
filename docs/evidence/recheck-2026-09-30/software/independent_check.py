"""Read-only independent check of saved simulation evidence; no production imports."""
from pathlib import Path
import csv, hashlib, json, math

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'simulations/results'
A = json.loads((ROOT / 'simulations/hardware-assumptions.json').read_text())
H = json.loads((OUT / 'hardware-summary.json').read_text())
C = json.loads((OUT / 'copper-resistance.json').read_text())
checks = []
for name, expected in H['source_sha256'].items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    checks.append({'check': 'source_hash', 'path': name, 'pass': actual == expected})
assert all(x['pass'] for x in checks), checks

def integrate(f, a, b, n=20000):
    h = (b-a)/n
    return h/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+i*h) for i in range(1,n)))

def ocv(soc):
    pts = A['ocv_points_soc_pct_v']
    for (s0,v0),(s1,v1) in zip(pts,pts[1:]):
        if s0 <= soc <= s1:
            return v0+(v1-v0)*(soc-s0)/(s1-s0)
    raise AssertionError(soc)

def bisection(f, lo, hi):
    assert f(lo)*f(hi) < 0
    for _ in range(80):
        mid = (lo+hi)/2
        if f(mid)*f(lo)>0: lo=mid
        else: hi=mid
    return (lo+hi)/2

rc = C['groups']['output_common']['R_35um_20C_ohm']+A['main_fuse_cold_ohm']+A['output_common_wiring_ohm']
rl = C['groups']['lamp_branch']['R_35um_20C_ohm']+A['branch_fuse_cold_ohm']+A['each_output_branch_wiring_ohm']
rf = C['groups']['fan_branch']['R_35um_20C_ohm']+A['branch_fuse_cold_ohm']+A['each_output_branch_wiring_ohm']+A['mosfet_room_on_ohm']

def output(fan):
    def currents(v):
        il = (v-math.sqrt(v*v-4*rl*2.5))/(2*rl)
        iff = (v-math.sqrt(v*v-4*rf*2.5))/(2*rf) if fan else 0
        return il, iff, .8/v
    v=bisection(lambda v: 5-v-rc*sum(currents(v)), 4,5)
    return 5*sum(currents(v)), v

power_on, rail_on = output(True)
starter = next(d for d in H['dc_cases'] if d['case']=='starter_2_5W_each')
assert abs(power_on-starter['converter_output_w']) < 1e-10
assert abs(rail_on-starter['rail_v']) < 1e-10
checks.append({'check': 'independent_5v_network_root', 'power_w': power_on, 'rail_v': rail_on, 'pass': True})

total_r = (A['battery_and_bms_resistance_ohm']+A['hv_wiring_contacts_external_fuse_ohm']+
           C['groups']['hv_loop']['R_35um_20C_ohm']+2*A['shunt_nominal_ohm'])
def dt_ds(s, power):
    e = ocv(s)
    # Direct quadratic formula; implementation uses a stable rationalized form.
    current = (e-math.sqrt(e*e-4*total_r*power/.9))/(2*total_r)
    return 6/(100*current)

baseline = integrate(lambda s: dt_ds(s,power_on),20,68)
assert abs(baseline-H['baseline']['runtime_to_common_endpoint_h'])*3600 < 1
checks.append({'check':'independent_baseline_quadrature','hours':baseline,
               'difference_seconds':3600*(H['baseline']['runtime_to_common_endpoint_h']-baseline),'pass':True})
with (OUT/'hardware-runtime-priority.csv').open() as f:
    rows=list(csv.DictReader(f))
shed=next(r for r in rows if r['fan_command_after_interval']=='False')
s=float(shed['true_soc_pct'])
power_off,_=output(False)
priority=integrate(lambda s: dt_ds(s,power_on),s,68)+integrate(lambda s: dt_ds(s,power_off),20,s)
assert abs(priority-H['priority']['runtime_to_common_endpoint_h'])*3600 < 1
checks.append({'check':'independent_priority_quadrature','hours':priority,'shed_soc_pct':s,
               'difference_seconds':3600*(H['priority']['runtime_to_common_endpoint_h']-priority),'pass':True})
energy = 6/100*integrate(ocv,20,68)
for policy in ['baseline','priority']:
    assert abs(energy-H[policy]['chemical_energy_wh']) < .002
checks.append({'check':'independent_OCV_charge_energy','wh':energy,'pass':True})

for case in H['startup_cases']:
    with (OUT/(case['case']+'.csv')).open() as f:
        rows=list(csv.DictReader(f))
    rows=[{k:float(v) for k,v in r.items()} for r in rows]
    r=min(rows,key=lambda r:abs(r['time']-.1))
    lamp_i=r['v(lamp)']/(5/case['lamp_current_at_5v_a'])
    fan_i=r['v(fan)']/(5/case['assumed_start_current_at_5v_a'])
    kcl=lamp_i+fan_i+.8/5-r['i(vregprobe)']
    common_drop=r['v(reg)']-r['v(rail)']-rc*r['i(vregprobe)']
    min_rail=min(x['v(rail)'] for x in rows)
    assert abs(kcl) < 1e-6
    assert abs(common_drop) < 1e-6
    assert abs(min_rail-case['min_rail_v']) < 1e-12
    assert case['rail_screen'] == ('PASS_MODEL_ONLY' if min_rail >= A['rail_screening_floor_v'] else 'FAIL_MODEL_ONLY')
    checks.append({'check':'startup_saved_trace_kcl','case':case['case'],'kcl_error_a':kcl,'pass':True})

report={'scope':'Independent algebra/quadrature/CSV/hash checks only; no physical hardware evidence.',
        'status':'PASS','checks':checks}
(Path(__file__).parent/'independent-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

