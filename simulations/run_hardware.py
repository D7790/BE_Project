"""Nonideal DC, discharge, copper and startup scenarios; never hardware evidence."""
from pathlib import Path
import csv
import datetime
import hashlib
import itertools
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulations.hardware_model import battery_point, interpolate_ocv, output_network
from simulations.ngspice_shared import Spice
from wattsense.model import Config, Controller

OUT = ROOT / 'simulations/results'
CIR = ROOT / 'simulations/circuits'
OUT.mkdir(exist_ok=True)
CIR.mkdir(exist_ok=True)
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT / 'hardware-summary.json').write_text(json.dumps({'status': 'RUNNING', 'started_utc': started,
                                                       'hardware_tested': False}))
PARAMS = ROOT / 'simulations/hardware-assumptions.json'
A = json.loads(PARAMS.read_text())
subprocess.run([os.environ.get('KICAD_PYTHON', r'C:\Program Files\KiCad\10.0\bin\python.exe'),
                str(ROOT / 'simulations/extract_copper.py')], check=True, cwd=ROOT)
COPPER = json.loads((OUT / 'copper-resistance.json').read_text())


def write_csv(name, rows):
    with (OUT / (name + '.csv')).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paths(stress=False):
    key = 'R_25um_60C_ohm' if stress else 'R_35um_20C_ohm'
    return {name: values[key] for name, values in COPPER['groups'].items()}


def output(fan_on, lamp=None, fan=None, stress=False):
    p = paths(stress)
    return output_network(
        A['lamp_reference_w'] if lamp is None else lamp,
        (A['fan_reference_w'] if fan is None else fan) if fan_on else 0,
        A['controller_and_sensors_5v_w'],
        p['output_common'] + A['main_fuse_cold_ohm'] + A['output_common_wiring_ohm'],
        p['lamp_branch'] + A['branch_fuse_cold_ohm'] + A['each_output_branch_wiring_ohm'],
        p['fan_branch'] + A['branch_fuse_cold_ohm'] + A['each_output_branch_wiring_ohm'] + A['mosfet_room_on_ohm'])


def battery(soc, output_w, efficiency=None, battery_r=None, stress=False):
    return battery_point(
        interpolate_ocv(soc, A['ocv_points_soc_pct_v']), output_w,
        A['converter_efficiency'] if efficiency is None else efficiency,
        A['battery_and_bms_resistance_ohm'] if battery_r is None else battery_r,
        A['hv_wiring_contacts_external_fuse_ohm'], paths(stress)['hv_loop'],
        A['shunt_nominal_ohm'] * (1 + A['shunt_tolerance_fraction'] if stress else 1))


dc = []
for name, on, lamp, fan, stress in [
        ('reference_3W_each', True, 3, 3, False),
        ('reference_fan_off', False, 3, 3, False),
        ('starter_2_5W_each', True, 2.5, 2.5, False),
        ('copper_and_shunt_corner', True, 3, 3, True)]:
    o = output(on, lamp, fan, stress)
    b = battery(68, o['converter_output_w'], stress=stress)
    assert abs(o['energy_balance_error_w']) < 1e-9
    assert abs(b['energy_balance_error_w']) < 1e-9
    dc.append({'case': name, **o, **b,
               'within_initial_branch_current_limit': max(o['lamp_a'], o['fan_a']) <= .6,
               'within_5v_continuous_limit': o['output_a'] <= 1.5,
               'fan_mosfet_conduction_w': o['fan_a']**2 * A['mosfet_room_on_ohm']})
write_csv('hardware-dc', dc)


def discharge(priority, capacity=None, efficiency=None, battery_r=None, save=None, dt=1., lamp=None, fan=None):
    """Measured capacity assumed known; no ADC errors/solar in these comparisons."""
    capacity = A['capacity_ah'] if capacity is None else capacity
    efficiency = A['converter_efficiency'] if efficiency is None else efficiency
    battery_r = A['battery_and_bms_resistance_ohm'] if battery_r is None else battery_r
    c = Controller(Config(capacity_ah=capacity, reserve_pct=A['reserve_pct']))
    c.synchronize(A['initial_soc_pct'])
    c.optional_on = True  # precondition: explicit safe restore already occurred
    truth = A['initial_soc_pct']
    samples, shed, fan_seconds = [], None, 0.
    total_chemical_wh, total_delivered_wh, max_balance = 0., 0., 0.
    lamp = A['starter_lamp_w'] if lamp is None else lamp
    fan = A['starter_fan_w'] if fan is None else fan
    output_by_state = {on: output(on, lamp, fan) for on in [True, False]}
    previous_state = None
    for index in range(1, int(24 * 3600 / dt) + 1):
        elapsed = index * dt
        fan_before = c.optional_on
        o = output_by_state[fan_before]
        b = battery(truth, o['converter_output_w'], efficiency, battery_r)
        truth -= 100 * b['battery_a'] * dt / (3600 * capacity)
        r = c.update(dt, b['battery_v'], b['battery_a'], b['load_sensor_w'], 28,
                     automatic=priority)
        assert c.soc_pct is not None and abs(c.soc_pct - truth) < 1e-8
        if fan_before:
            fan_seconds += dt
        if priority and fan_before and not c.optional_on and shed is None:
            shed = elapsed
        total_chemical_wh += b['chemical_power_w'] * dt / 3600
        total_delivered_wh += o['delivered_w'] * dt / 3600
        max_balance = max(max_balance, abs(b['energy_balance_error_w']), abs(o['energy_balance_error_w']))
        stop = truth <= c.config.reserve_pct or b['battery_v'] <= c.config.low_operating_v
        if save and (index % max(1, round(60 / dt)) == 0 or r['state'] != previous_state or stop):
            samples.append({'time_s': elapsed, 'true_soc_pct': truth, 'estimated_soc_pct': c.soc_pct,
                            'battery_v': b['battery_v'], 'buck_input_v': b['buck_input_v'],
                            'battery_a': b['battery_a'], 'load_sensor_w': b['load_sensor_w'],
                            'rail_v': o['rail_v'], 'delivered_w': o['delivered_w'],
                            'fan_during_interval': fan_before, 'fan_command_after_interval': c.optional_on,
                            'state': r['state']})
        previous_state = r['state']
        if stop:
            break
    else:
        raise AssertionError('No common endpoint reached in 24 h')
    if save:
        write_csv(save, samples)
    return {'runtime_to_common_endpoint_h': elapsed / 3600, 'fan_service_h': fan_seconds / 3600,
            'shed_h': None if shed is None else shed / 3600,
            'capacity_ah': capacity, 'efficiency': efficiency, 'battery_r_ohm': battery_r,
            'lamp_delivered_w': lamp, 'fan_delivered_w': fan,
            'controller_delivered_w': A['controller_and_sensors_5v_w'],
            'initial_soc_pct': A['initial_soc_pct'], 'reserve_pct': A['reserve_pct'],
            'chemical_energy_wh': total_chemical_wh, 'delivered_energy_wh': total_delivered_wh,
            'max_power_balance_error_w': max_balance, 'integration_step_s': dt,
            'endpoint': (f'{c.config.reserve_pct:g}% true SOC' if truth <= c.config.reserve_pct
                         else f'{c.config.low_operating_v:g} V operating threshold')}


baseline = discharge(False, save='hardware-runtime-baseline')
priority = discharge(True, save='hardware-runtime-priority')
reference_3w = {'baseline': discharge(False, lamp=3, fan=3),
                'priority': discharge(True, lamp=3, fan=3),
                'note': 'Comparison with earlier 3 W loads only; these DC branch currents exceed the initial 0.6 A target.'}
convergence = []
for automatic, reference in [(False, baseline), (True, priority)]:
    fine = discharge(automatic, dt=.25)
    error_s = abs(fine['runtime_to_common_endpoint_h'] - reference['runtime_to_common_endpoint_h']) * 3600
    assert error_s <= 2
    convergence.append({'priority': automatic, 'coarse_step_s': 1, 'fine_step_s': .25,
                        'runtime_difference_s': error_s})
sweep = []
for capacity, efficiency, resistance in itertools.product([4.8, 6.], [.8, .9, .95], [.05, .1, .2]):
    base = discharge(False, capacity, efficiency, resistance)
    controlled = discharge(True, capacity, efficiency, resistance)
    assert controlled['runtime_to_common_endpoint_h'] > base['runtime_to_common_endpoint_h']
    sweep.append({'capacity_ah': capacity, 'efficiency': efficiency, 'battery_r_ohm': resistance,
                  'baseline_h': base['runtime_to_common_endpoint_h'],
                  'priority_h': controlled['runtime_to_common_endpoint_h'],
                  'fan_service_h': controlled['fan_service_h']})
write_csv('hardware-runtime-sensitivity', sweep)

# Behavioural source screening: static finite output resistance and current limit.
# No PWM/loop model, no fuse-opening, no motor startup/restart state machine.
spice = Spice()
startup = []
p = paths()
common_r = p['output_common'] + A['main_fuse_cold_ohm'] + A['output_common_wiring_ohm']
lamp_r = p['lamp_branch'] + A['branch_fuse_cold_ohm'] + A['each_output_branch_wiring_ohm']
fan_r = p['fan_branch'] + A['branch_fuse_cold_ohm'] + A['each_output_branch_wiring_ohm'] + A['mosfet_room_on_ohm']
for name, peak_a, limit_a, capacitance_uf, lamp_a, fan_run_a in [
        ('startup_no_surge', .6, 2., 470, .6, .6),
        ('startup_2x_2A', 1.2, 2., 470, .6, .6),
        ('startup_3x_1_5A', 1.8, 1.5, 470, .6, .6),
        ('startup_3x_1_5A_large_cap', 1.8, 1.5, 2200, .6, .6),
        ('startup_3x_3A', 1.8, 3., 470, .6, .6),
        ('startup_starter_2x_2A', 1.0, 2., 470, .5, .5)]:
    source_r = A['startup_model_regulator_output_r_ohm']
    esr = A['startup_model_capacitor_esr_ohm']
    duration = A['startup_model_duration_s']
    netlist = f'''Wattsense bounded fan-start supply scenario {name}
* ASSUMED equivalent supply; NOT LM2596 component model or selected module.
* Resistive fan demand at 5V: {peak_a} A for {duration} s, then {fan_run_a} A.
* Capacitance includes an assumed external module capacitor, not just PCB C11.
* Fuses remain resistors; no trip or pulse-life claim.
Breg 0 supply I=max(0,min({limit_a},(5-v(reg))/{source_r}))
Vregprobe supply reg 0
Resr reg cap {esr}
Cout cap 0 {capacitance_uf}u
Rcommon reg rail {common_r}
Rlampfeed rail lamp {lamp_r}
Rlamp lamp 0 {5/lamp_a}
Icontroller rail 0 {A['controller_and_sensors_5v_w']/5}
Rfanfeed rail fan {fan_r}
Vfanprobe fan demand 0
Bfan demand 0 I=v(demand)*(time < 0.01 ? 0 : (time < {0.01+duration} ? {peak_a/5} : {fan_run_a/5}))
.options reltol=1e-5
.tran 20u 150m 0 20u
.end
'''
    (CIR / (name + '.cir')).write_text(netlist)
    values = spice.run(netlist, ['time', 'v(reg)', 'v(rail)', 'v(lamp)', 'v(fan)', 'i(vregprobe)', 'i(vfanprobe)'])
    (OUT / (name + '.log')).write_text('\n'.join(spice.log))
    write_csv(name, [dict(zip(values, row)) for row in zip(*values.values())])
    # At 90 ms after start the capacitor has settled: compare independent DC KCL.
    conductance = 1 / (5 / lamp_a + lamp_r) + 1 / (5 / peak_a + fan_r)
    controller_a = A['controller_and_sensors_5v_w'] / 5
    unconstrained_rail = (5 - (source_r + common_r) * controller_a) / (1 + (source_r + common_r) * conductance)
    ideal_current = unconstrained_rail * conductance + controller_a
    expected = unconstrained_rail if ideal_current <= limit_a else (limit_a - controller_a) / conductance
    nearest = min(range(len(values['time'])), key=lambda n: abs(values['time'][n] - .10))
    assert abs(values['v(rail)'][nearest] - expected) < .005
    minimum = min(values['v(rail)'])
    assert max(values['i(vregprobe)']) <= limit_a + 1e-6
    assert values['v(rail)'][-1] > A['rail_screening_floor_v']
    startup.append({'case': name, 'assumed_start_current_at_5v_a': peak_a,
                    'lamp_current_at_5v_a': lamp_a, 'fan_run_current_at_5v_a': fan_run_a,
                    'assumed_supply_limit_a': limit_a, 'assumed_module_capacitance_uf': capacitance_uf,
                    'min_rail_v': minimum, 'min_fan_terminal_v': min(values['v(fan)']),
                    'peak_supply_a': max(values['i(vregprobe)']),
                    'rail_screening_floor_v': A['rail_screening_floor_v'],
                    'rail_screen': 'PASS_MODEL_ONLY' if minimum >= A['rail_screening_floor_v'] else 'FAIL_MODEL_ONLY',
                    'steady_startup_rail_analytic_v': expected,
                    'steady_startup_rail_spice_v': values['v(rail)'][nearest]})
assert startup[0]['rail_screen'] == 'PASS_MODEL_ONLY'
assert startup[2]['rail_screen'] == startup[3]['rail_screen'] == 'FAIL_MODEL_ONLY'

summary = {
    'status': 'CHECKS_PASS', 'hardware_tested': False, 'started_utc': started,
    'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'provenance': 'SIMULATION ONLY. No physical prototype tested.',
    'scope': 'Lumped battery and converter efficiency, selected PCB copper paths, DC loss and '
             'constant-power discharge. Six separate behavioural startup circuits. '
             'No complete ESP32/BMS/charger/BLDC/PWM/thermal/EMC simulation.',
    'dc_cases': dc, 'baseline': baseline, 'priority': priority, 'earlier_3w_load_comparison': reference_3w,
    'runtime_extension_pct': 100 * (priority['runtime_to_common_endpoint_h'] / baseline['runtime_to_common_endpoint_h'] - 1),
    'convergence_checks': convergence, 'sensitivity_pairs': sweep,
    'startup_cases': startup,
    'copper': COPPER['groups'],
    'source_sha256': {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
                      for f in [PARAMS, Path(__file__), ROOT / 'simulations/hardware_model.py',
                                ROOT / 'simulations/extract_copper.py', ROOT / 'wattsense/model.py']},
    'pcb_sha256': COPPER['pcb_sha256'],
}
(OUT / 'hardware-summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({'dc_cases': dc, 'baseline': baseline, 'priority': priority,
                  'convergence': convergence, 'sensitivity_pairs': len(sweep), 'startup': startup}, indent=2))
