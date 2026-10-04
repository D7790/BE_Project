"""Independent publication evidence checks; never imports project model code.

Reads current source/data/CAD and writes only in this recheck directory.
Run fresh KiCad ERC/DRC separately; command provenance is recorded below.
"""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import math
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAD = ROOT / 'hardware/pcb/wattsense-main-revB-4layer'
RESULTS = ROOT / 'simulations/results'
checks = []
inputs = {}


def data(path):
    content = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(content).hexdigest()
    return content


def document(path):
    return json.loads(data(path))


def rows(name):
    return list(csv.DictReader(data(RESULTS / name).decode().splitlines()))


def check(name, passed, **details):
    checks.append({'check': name, 'pass': bool(passed), **details})


record = document(ROOT / 'docs/evidence/final-audit-record.json')
for group, base in [('source_sha256', ROOT), ('cad_native_sha256', CAD),
                    ('evidence_sha256', ROOT), ('document_sha256', ROOT)]:
    mismatches = []
    for name, expected in record[group].items():
        actual = hashlib.sha256(data(base / name)).hexdigest()
        if actual != expected:
            mismatches.append({'path': name, 'expected': expected, 'actual': actual})
    check(group + '_matches_28_Sep_checkpoint', not mismatches,
          files=len(record[group]), mismatches=mismatches)

archive = CAD / 'exports/wattsense-main-revB-4layer-prototype.zip'
digest = hashlib.sha256(data(archive)).hexdigest()
check('archive_matches_28_Sep_checkpoint', digest == record['archive_sha256'], sha256=digest)
with zipfile.ZipFile(archive) as z:
    check('archive_CRC_and_entry_count', z.testzip() is None and len(z.namelist()) == 15,
          count=len(z.namelist()))
    source = json.loads(z.read('SOURCE-VALIDATION.json'))
    power = json.loads(z.read('POWER-PATH-VALIDATION.json'))
    check('archive_source_hash_manifest', all(hashlib.sha256(data(CAD / name)).hexdigest() == expected
          for name, expected in source['sha256'].items()), entries=len(source['sha256']))
    check('archive_power_path_source_hashes',
          power['pcb_sha256'] == hashlib.sha256(data(CAD / 'wattsense-main.kicad_pcb')).hexdigest()
          and power['script_sha256'] == hashlib.sha256(data(CAD / 'tools/check_power_paths.py')).hexdigest())
    fabrications = [name for name in z.namelist() if name.startswith('wattsense-main-')]
    check('archive_matches_saved_fabrication_bytes', len(fabrications) == 12 and
          all(z.read(name) == data(CAD / 'exports/gerbers' / name) for name in fabrications),
          fabrication_files=len(fabrications))
    check('archive_instruction_and_audit_contents_match',
          z.read('FABRICATION.md') == data(CAD / 'FABRICATION.md')
          and source == document(CAD / 'reports/connectivity-audit.json')
          and power == document(CAD / 'reports/power-path-audit.json'))

erc = document(HERE / 'erc.json')
drc = document(HERE / 'drc.json')
check('fresh_readonly_KiCad_ERC', not any(s['violations'] for s in erc['sheets']),
      violation_count=sum(len(s['violations']) for s in erc['sheets']),
      ignored_checks=erc.get('ignored_checks', []))
check('fresh_readonly_KiCad_DRC_and_parity', not (drc['violations'] or drc['unconnected_items'] or drc['schematic_parity']),
      violation_count=len(drc['violations']), unconnected=len(drc['unconnected_items']),
      schematic_parity=len(drc['schematic_parity']), ignored_checks=drc.get('ignored_checks', []))

config = data(ROOT / 'firmware/include/config.h').decode()
flags = {name: re.search(r'constexpr bool ' + name + r' = (true|false);', config).group(1) == 'true'
         for name in ['HARDWARE_CONFIRMED', 'SOLAR_SENSOR_FITTED']}
check('production_physical_control_and_solar_remain_disabled', not any(flags.values()), flags=flags)

h = document(RESULTS / 'hardware-summary.json')
a = document(ROOT / 'simulations/hardware-assumptions.json')
copper = document(RESULTS / 'copper-resistance.json')
check('hardware_model_explicit_provenance', h['status'] == 'CHECKS_PASS' and h['hardware_tested'] is False,
      scope=h['scope'])
check('hardware_summary_source_hashes', all(hashlib.sha256(data(ROOT / name)).hexdigest() == expected
      for name, expected in h['source_sha256'].items()))
for name, key in [('hardware-dc.csv', 'dc_cases'), ('hardware-runtime-sensitivity.csv', 'sensitivity_pairs')]:
    raw = rows(name)
    table = h[key]
    match = len(raw) == len(table)
    max_error = 0
    for left, right in zip(raw, table):
        for column, actual in left.items():
            expected = right[column]
            if isinstance(expected, bool):
                match = match and actual == str(expected)
            elif isinstance(expected, (int, float)):
                error = abs(float(actual) - expected)
                max_error = max(max_error, error)
                match = match and error < 1e-10
            else:
                match = match and actual == expected
    check('table_matches_raw_' + name, match, rows=len(raw), maximum_numeric_error=max_error)

runtime_rows = {}
for mode in ['baseline', 'priority']:
    raw = rows('hardware-runtime-' + mode + '.csv')
    runtime_rows[mode] = raw
    end = raw[-1]
    check(mode + '_raw_endpoint_matches_summary',
          abs(float(end['time_s']) / 3600 - h[mode]['runtime_to_common_endpoint_h']) < 1e-12
          and float(end['true_soc_pct']) <= a['reserve_pct'] and end['state'] == 'RESERVE',
          time_s=float(end['time_s']), final_soc_pct=float(end['true_soc_pct']))
    check(mode + '_ideal_current_counting_matches_truth',
          all(abs(float(x['true_soc_pct']) - float(x['estimated_soc_pct'])) < 1e-8 for x in raw),
          warning='This checks an exact-capacity/no-sensor-error scenario, not physical SOC accuracy.')

shed_rows = [r for r in runtime_rows['priority'] if r['fan_during_interval'] == 'True'
             and r['fan_command_after_interval'] == 'False']
check('priority_shedding_event_matches_raw', len(shed_rows) == 1 and
      abs(float(shed_rows[0]['time_s']) / 3600 - h['priority']['shed_h']) < 1e-12)

# Independent scalar bisection for the 5 V constant-power circuit.
p = {name: values['R_35um_20C_ohm'] for name, values in copper['groups'].items()}
rc = p['output_common'] + a['main_fuse_cold_ohm'] + a['output_common_wiring_ohm']
rl = p['lamp_branch'] + a['branch_fuse_cold_ohm'] + a['each_output_branch_wiring_ohm']
rf = p['fan_branch'] + a['branch_fuse_cold_ohm'] + a['each_output_branch_wiring_ohm'] + a['mosfet_room_on_ohm']


def current(volts, resistance, watts):
    return 2 * watts / (volts + math.sqrt(volts**2 - 4 * resistance * watts))


def output_power(fan_on):
    lo, hi = 3., 5.
    fan_w = a['starter_fan_w'] if fan_on else 0
    for _ in range(80):
        v = (lo + hi) / 2
        amps = current(v, rl, a['starter_lamp_w']) + current(v, rf, fan_w) + a['controller_and_sensors_5v_w'] / v
        if v + rc * amps > 5:
            hi = v
        else:
            lo = v
    return v, 5 * amps


rail, output_w = output_power(True)
dc_starter = next(item for item in h['dc_cases'] if item['case'] == 'starter_2_5W_each')
check('independent_5V_bisection', abs(rail - dc_starter['rail_v']) < 1e-10 and
      abs(output_w - dc_starter['converter_output_w']) < 1e-10, rail_v=rail, output_w=output_w)


def ocv(soc):
    points = a['ocv_points_soc_pct_v']
    for (s0, v0), (s1, v1) in zip(points, points[1:]):
        if soc <= s1:
            return v0 + (v1 - v0) * (soc - s0) / (s1 - s0)
    raise ValueError('Outside independent integration interval')


def integrate(function, lower, upper, count=9600):
    step = (upper - lower) / count
    total = function(lower) + function(upper)
    total += 4 * sum(function(lower + i * step) for i in range(1, count, 2))
    total += 2 * sum(function(lower + i * step) for i in range(2, count, 2))
    return total * step / 3


resistance = (a['battery_and_bms_resistance_ohm'] + a['hv_wiring_contacts_external_fuse_ohm']
              + p['hv_loop'] + 2 * a['shunt_nominal_ohm'])


def runtime_between(lower, upper, fan_on):
    watts = output_power(fan_on)[1] / a['converter_efficiency']
    return a['capacity_ah'] / 100 * integrate(lambda soc: 1 / current(ocv(soc), resistance, watts), lower, upper)


shed_soc = float(shed_rows[0]['true_soc_pct'])
analytic_baseline = runtime_between(a['reserve_pct'], a['initial_soc_pct'], True)
analytic_priority = (runtime_between(shed_soc, a['initial_soc_pct'], True)
                     + runtime_between(a['reserve_pct'], shed_soc, False))
for mode, analytic in [('baseline', analytic_baseline), ('priority', analytic_priority)]:
    difference_s = abs(analytic - h[mode]['runtime_to_common_endpoint_h']) * 3600
    check('independent_Simpson_runtime_' + mode, difference_s < 1.,
          independent_h=analytic, difference_s=difference_s)
energy_wh = a['capacity_ah'] / 100 * integrate(ocv, a['reserve_pct'], a['initial_soc_pct'])
check('independent_OCV_integral_energy', all(abs(h[mode]['chemical_energy_wh'] - energy_wh) < .002
      for mode in ['baseline', 'priority']), independent_chemical_energy_wh=energy_wh)

for case in h['startup_cases']:
    raw = rows(case['case'] + '.csv')
    min_rail = min(float(x['v(rail)']) for x in raw)
    min_fan = min(float(x['v(fan)']) for x in raw)
    max_i = max(float(x['i(vregprobe)']) for x in raw)
    match = max(abs(min_rail - case['min_rail_v']), abs(min_fan - case['min_fan_terminal_v']),
                abs(max_i - case['peak_supply_a'])) < 1e-10
    check(case['case'] + '_raw_extrema', match, minimum_rail_v=min_rail,
          minimum_fan_terminal_v=min_fan, peak_supply_a=max_i,
          model_screen=case['rail_screen'])
    steady = min(raw, key=lambda x: abs(float(x['time']) - .1))
    v = float(steady['v(rail)'])
    expected_amps = (v / (5 / case['lamp_current_at_5v_a'] + rl)
                     + v / (5 / case['assumed_start_current_at_5v_a'] + rf)
                     + a['controller_and_sensors_5v_w'] / 5)
    error = float(steady['i(vregprobe)']) - expected_amps
    check(case['case'] + '_steady_KCL', abs(error) < 1e-6, error_a=error)

base, priority = h['baseline'], h['priority']
publication_numbers = {
    'lamp_baseline_h': base['runtime_to_common_endpoint_h'],
    'lamp_priority_h': priority['runtime_to_common_endpoint_h'],
    'fan_baseline_h': base['fan_service_h'],
    'fan_priority_h': priority['fan_service_h'],
    'lamp_service_gain_pct': 100 * (priority['runtime_to_common_endpoint_h'] / base['runtime_to_common_endpoint_h'] - 1),
    'fan_service_reduction_pct': 100 * (1 - priority['fan_service_h'] / base['fan_service_h']),
    'lamp_delivered_energy_gain_wh': a['starter_lamp_w'] * (priority['runtime_to_common_endpoint_h'] - base['runtime_to_common_endpoint_h']),
    'fan_delivered_energy_reduction_wh': a['starter_fan_w'] * (base['fan_service_h'] - priority['fan_service_h']),
    'total_delivered_energy_baseline_wh': base['delivered_energy_wh'],
    'total_delivered_energy_priority_wh': priority['delivered_energy_wh'],
    'sensitivity_pairs': len(h['sensitivity_pairs']),
    'sensitivity_baseline_h_range': [min(r['baseline_h'] for r in h['sensitivity_pairs']), max(r['baseline_h'] for r in h['sensitivity_pairs'])],
    'sensitivity_priority_h_range': [min(r['priority_h'] for r in h['sensitivity_pairs']), max(r['priority_h'] for r in h['sensitivity_pairs'])],
    'startup_model_screen_pass': sum(r['rail_screen'] == 'PASS_MODEL_ONLY' for r in h['startup_cases']),
    'startup_model_screen_fail': sum(r['rail_screen'] == 'FAIL_MODEL_ONLY' for r in h['startup_cases']),
}
result = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS' if all(c['pass'] for c in checks) else 'REVIEW_REQUIRED',
    'scope': 'Independent hashes, archive/CAD reports, CSV/summary comparisons, algebra and numerical quadrature. No physical measurements.',
    'hardware_tested': False,
    'kiCad_commands': [
        'kicad-cli sch erc <native_schematic> --format json --severity-all --exit-code-violations -o paper/evidence/recheck/erc.json',
        'kicad-cli pcb drc <native_pcb> --schematic-parity --format json --severity-all --exit-code-violations --refill-zones -o paper/evidence/recheck/drc.json',
    ],
    'cad_was_saved': False,
    'checks': checks,
    'publication_numbers': publication_numbers,
    'critical_scope_limits': [
        'Simulation/design study only: no assembled board, calibration results, cell tests, or measured runtime.',
        'The OCV curve, battery/wiring resistances, converter efficiency, startup demand and capacitance are illustrative assumptions.',
        'Battery capacity and current counting are exact in the runtime comparison; no stochastic uncertainty, measured validation, or statistical significance is claimed.',
        'Only selected F.Cu paths are modelled; ground planes, pad spreading, vias, parasitic inductance and thermal feedback are omitted.',
        'Startup supply is an instantaneous behavioural current limiter; fan is voltage-dependent resistance, not a selected BLDC device model.',
        '4.75 V is a provisional common-rail screen and does not establish ESP32 reset limits or fan terminal-voltage compatibility.',
        'Reduced startup cases use different load behaviours from constant-power discharge/DC cases and must not be merged into one validated model.',
        'Essential load remains powered at reserve; the model stops the trial externally. This is not full battery protection.',
        'No live solar-harvesting, MPPT, cloud/AI, custom BMS, cell balancing, EMC/thermal or safety-certification claim.',
        'Runtime gain is service reallocation with less fan service, not increased battery capacity or equal-service efficiency improvement.',
        '18 deterministic sensitivity pairs are scenarios, not repeated trials or confidence intervals.',
    ],
    'inputs_sha256': inputs,
}
(HERE / 'publication-evidence-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'status': result['status'], 'checks': len(checks),
                  'failed_checks': [c for c in checks if not c['pass']],
                  'publication_numbers': publication_numbers}, indent=2))
