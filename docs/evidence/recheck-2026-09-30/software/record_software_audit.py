"""Record current rerun and independent checks, preserving the previous run."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
RESULTS = ROOT / 'simulations/results'
BEFORE = OUT.parent / 'before-results'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
suite = json.loads((RESULTS/'suite-summary.json').read_text())
assert suite['status'] == 'PASS' and not suite['hardware_tested']
assert all(x['exit_code'] == 0 for x in suite['checks'])
assert all(digest(ROOT/name) == sha for name, sha in suite['source_sha256'].items())
checks.append({'check': 'suite_sources_current', 'source_count': len(suite['source_sha256']), 'pass': True})
testlog = (RESULTS/'python-tests.log').read_text()
count = int(re.search(r'Ran (\d+) tests', testlog)[1])
assert re.search(r'\nOK\s*$', testlog)
host = json.loads((RESULTS/'firmware-host-summary.json').read_text())
native = sum(x['assertions'] for x in host['results']) + host['register_reader']['assertions']
assert not host['production_hardware_confirmed']
spice = json.loads((RESULTS/'spice-summary.json').read_text())
hardware = json.loads((RESULTS/'hardware-summary.json').read_text())
system = json.loads((RESULTS/'system-summary.json').read_text())
independent = json.loads((OUT/'independent-check.json').read_text())
parity = json.loads((OUT/'policy-differential.json').read_text())
assert independent['status'] == parity['status'] == 'PASS'
assert hardware['status'] == 'CHECKS_PASS' and not hardware['hardware_tested']
assert all(case['status'] == 'PASS' for case in spice['cases'][:3])
for case in spice['cases'][3:]:
    expected = 'PASS' if case['rise_30_70_ns'] <= case['standard_mode_limit_ns'] else 'OUTSIDE_ENVELOPE'
    assert case['status'] == expected

def without_timestamps(value):
    if isinstance(value, dict):
        return {k: without_timestamps(v) for k, v in value.items()
                if k not in ('started_utc', 'finished_utc')}
    if isinstance(value, list):
        return [without_timestamps(x) for x in value]
    return value

reproduced = []
for name in ('suite-summary.json', 'firmware-host-summary.json', 'spice-summary.json',
             'system-summary.json', 'hardware-summary.json', 'copper-resistance.json'):
    old = json.loads((BEFORE/name).read_text())
    new = json.loads((RESULTS/name).read_text())
    matches = without_timestamps(old) == without_timestamps(new)
    assert matches, name
    reproduced.append({'file': name, 'unchanged_except_run_timestamps': matches})
csvs = sorted(RESULTS.glob('*.csv'))
csv_matches = [p.name for p in csvs if (BEFORE/p.name).exists() and digest(p) == digest(BEFORE/p.name)]
assert len(csv_matches) == len(csvs)
builds = []
for target in ('esp32dev', 'bringup'):
    log_bytes = (OUT/f'build-{target}.log').read_bytes()
    log = log_bytes.decode('utf-16' if log_bytes.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
    assert '[SUCCESS]' in log
    sizes = re.findall(r'(RAM|Flash):.*used (\d+) bytes from (\d+) bytes', log)
    builds.append({'target': target, 'status': 'PASS',
                   'memory': {kind.lower(): {'used_bytes': int(used), 'capacity_bytes': int(cap)}
                              for kind, used, cap in sizes},
                   'binary_sha256': {ext: digest(ROOT/f'firmware/.pio/build/{target}/firmware.{ext}')
                                     for ext in ('bin', 'elf')}})
snapshot = OUT/'result-summaries'
snapshot.mkdir(exist_ok=True)
for p in RESULTS.iterdir():
    if p.suffix in ('.json', '.log'):
        shutil.copy2(p, snapshot/p.name)
report = {
    'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS_WITH_HARDWARE_VALIDATION_PENDING',
    'python_tests': count, 'native_cpp_assertions': native,
    'original_spice_cases': len(spice['cases']),
    'original_spice_outside_envelope': [case['case'] for case in spice['cases'] if case['status'] != 'PASS'],
    'nonideal_startup_cases': len(hardware['startup_cases']),
    'nonideal_runtime_sensitivity_pairs': len(hardware['sensitivity_pairs']),
    'checks': checks, 'independent_numeric_checks': len(independent['checks']),
    'cpp_python_differential_samples': parity['sample_comparisons'],
    'builds': builds, 'reproduced_summaries': reproduced,
    'byte_identical_csv_count': len(csv_matches),
    'production_source_changes': [], 'hardware_tested': False, 'flashed': False,
    'source_sha256': suite['source_sha256'],
    'result_sha256': {p.name: digest(p) for p in RESULTS.iterdir() if p.is_file()},
    'limitations': [
        'Both builds are compile/link evidence only; no ESP32 or physical board exercised.',
        'Host policy and Python agree over this deterministic input corpus, not all possible inputs.',
        'Whole-system model executes the Python policy; the separately tested C++ controller is not coupled to SPICE.',
        'OCV, capacity, resistance, efficiency and startup loads remain unmeasured assumptions.',
        'Three startup cases intentionally fail the provisional 4.75 V rail screen; larger capacitor does not cure sustained overload.',
        'The comparison using 4.7 kohm I2C pull-ups at 400 pF is outside the 1 us screen; the current PCB uses 2.2 kohm.',
        'Runtime prioritisation trades fan service for lamp service and is not an efficiency or capacity gain.',
        'Firmware remains HARDWARE_CONFIRMED=false; no firmware was flashed or hardware armed.',
    ],
}
(OUT/'software-audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k not in ('source_sha256', 'result_sha256')}, indent=2))
