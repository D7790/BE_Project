"""Read-only manuscript arithmetic review against saved current evidence."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MS = ROOT / 'paper/src/manuscript.json'
manuscript_bytes = MS.read_bytes()
m = json.loads(manuscript_bytes)
h = json.loads((ROOT / 'simulations/results/hardware-summary.json').read_text())
checks = []


def check(name, result, **details):
    checks.append({'check': name, 'pass': bool(result), **details})


b, p = h['baseline'], h['priority']
base_h, priority_h = b['runtime_to_common_endpoint_h'], p['runtime_to_common_endpoint_h']
lamp_gain = 100 * (priority_h / base_h - 1)
fan_lost = 100 * (1 - p['fan_service_h'] / b['fan_service_h'])
for name, number, digits in [('baseline', base_h, 3), ('priority', priority_h, 3),
                             ('priority_fan', p['fan_service_h'], 3),
                             ('lamp_gain', lamp_gain, 2), ('fan_loss', fan_lost, 2)]:
    check('abstract_' + name, f'{number:.{digits}f}' in m['abstract'], value=number)

tables = {block['number']: block for block in m['blocks'] if block['type'] == 'table'}
expected_table2 = [
    [f'{base_h:.4f}', f'{priority_h:.4f}'],
    [f'{b["fan_service_h"]:.4f}', f'{p["fan_service_h"]:.4f}'],
    [f'{2.5 * (base_h + b["fan_service_h"]):.4f}', f'{2.5 * (priority_h + p["fan_service_h"]):.4f}'],
    [f'{b["delivered_energy_wh"]:.4f}', f'{p["delivered_energy_wh"]:.4f}'],
    [f'{b["chemical_energy_wh"]:.2f}', f'{p["chemical_energy_wh"]:.2f}'],
]
for row, expected in zip(tables['II']['rows'], expected_table2):
    check('table_II_' + row[0], row[1:] == expected, actual=row[1:], expected=expected)

claims = {block['id']: block['text'] for block in m['blocks'] if block.get('id')}
with (ROOT / 'simulations/results/hardware-runtime-priority.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
shed = next(r for r in rows if r['fan_during_interval'] == 'True' and r['fan_command_after_interval'] == 'False')
heuristic_h = (float(shed['estimated_soc_pct']) - 20) * .01 * 6 * 12.8 / float(shed['load_sensor_w'])
counterfactual_h = base_h - float(shed['time_s']) / 3600
overestimate_s = (heuristic_h - counterfactual_h) * 3600
check('C027_heuristic', f'{heuristic_h:.4f}' in claims['C027'], value_h=heuristic_h)
check('C027_counterfactual', f'{counterfactual_h:.4f}' in claims['C027'], value_h=counterfactual_h)
check('C027_approximate_seconds', str(round(overestimate_s)) in claims['C027'], difference_s=overestimate_s)
check('C025_service_changes', f'{priority_h - base_h:.4f}' in claims['C025'] and
      f'{b["fan_service_h"] - p["fan_service_h"]:.4f}' in claims['C025'])
dc = next(row for row in h['dc_cases'] if row['case'] == 'starter_2_5W_each')
dc_fields = ['output_a', 'battery_a', 'rail_v', 'lamp_v', 'fan_v', 'converter_loss_w',
             'output_path_loss_w', 'two_shunts_loss_w']
check('C028_DC_numbers', all(f'{dc[name]:.4f}' in claims['C028'] for name in dc_fields))
check('C029_sensitivity_ranges', all(f'{value:.4f}' in claims['C029'] for value in [
    min(r['baseline_h'] for r in h['sensitivity_pairs']), max(r['baseline_h'] for r in h['sensitivity_pairs']),
    min(r['priority_h'] for r in h['sensitivity_pairs']), max(r['priority_h'] for r in h['sensitivity_pairs'])]))
host = json.loads((ROOT / 'simulations/results/firmware-host-summary.json').read_text())
assertions = sum(row['assertions'] for row in host['results']) + host['register_reader']['assertions']
py_log = (ROOT / 'simulations/results/python-tests.log').read_text()
py_count = int(re.search(r'Ran (\d+) tests', py_log).group(1))
independent = json.loads((HERE / 'publication-evidence-check.json').read_text())
check('C033_check_counts', all(str(n) in claims['C033'] for n in [py_count, assertions, len(independent['checks'])])
      and independent['status'] == 'PASS', python_tests=py_count, cpp_assertions=assertions,
      saved_independent_checks=len(independent['checks']))
check('C034_convergence', all(f'{r["runtime_difference_s"]:.2f}' in claims['C034'] for r in h['convergence_checks']))

report = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS_NUMERIC_COMPARISONS' if all(c['pass'] for c in checks) else 'REVIEW_REQUIRED',
    'manuscript_sha256': hashlib.sha256(manuscript_bytes).hexdigest(),
    'checks': checks,
    'scope': 'Numeric roundoff consistency against current saved traces, summaries and test logs; not human source verification or physical validation.',
    'counterfactual_details': {'heuristic_h': heuristic_h, 'same_load_remaining_h': counterfactual_h,
                               'overestimate_s': overestimate_s},
}
(HERE / 'manuscript-numeric-review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'status': report['status'], 'checks': len(checks),
                  'failed': [c for c in checks if not c['pass']], 'manuscript_sha256': report['manuscript_sha256'],
                  'counterfactual': report['counterfactual_details']}, indent=2))
