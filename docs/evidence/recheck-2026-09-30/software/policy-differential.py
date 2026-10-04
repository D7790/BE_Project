"""Fresh deterministic differential audit; production files are never edited.

Compare compiled controller.h with the Python reference over varied healthy
sample sequences. Boundary, transaction-fault and hardware-lock tests remain
the responsibility of the main host test suite. This is not an ESP32 emulator.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import random
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from wattsense.model import Controller

OUT = Path(__file__).parent
WORK = ROOT / '.local' / 'recheck-2026-09-30-policy'
WORK.mkdir(exist_ok=True)
production = ROOT / 'firmware/include'
before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (production/'controller.h', production/'config.h')}
(WORK/'controller.h').write_bytes((production/'controller.h').read_bytes())
(WORK/'config.h').write_text((production/'config.h').read_text().replace(
    'constexpr bool HARDWARE_CONFIRMED = false;',
    'constexpr bool HARDWARE_CONFIRMED = true;'))
cpp = r'''#include <iostream>
#include <iomanip>
#include "controller.h"
int main() {
    int n; std::cin >> n;
    std::cout << std::setprecision(14);
    for (int caseNo=0; caseNo<n; ++caseNo) {
        Controller c; double initial; int steps;
        std::cin >> initial >> steps; c.socPct=initial; c.optionalOn=true;
        for (int k=0; k<steps; ++k) {
            Sample s; float dt;
            std::cin >> dt >> s.batteryV >> s.batteryA >> s.loadW >> s.temperatureC >> c.minimumRuntimeH;
            s.valid=true; c.update(s, dt);
            std::cout << c.socPct << ' ' << c.energyWh << ' ' << c.runtimeH << ' '
                << c.noSolarRuntimeH << ' ' << c.optionalOn << ' ' << c.state << '\n';
        }
    }
}
'''
(OUT/'policy-differential.cpp').write_text(cpp)
(WORK/'audit.cpp').write_text(cpp)
compiler = ROOT / '.local/platformio/packages/toolchain-gccmingw32/bin/g++.exe'
env = os.environ.copy()
env['PATH'] = str(compiler.parent) + os.pathsep + env.get('PATH', '')
subprocess.run([str(compiler), '-std=c++11', '-O2', '-Wall', '-Wextra',
                '-static-libgcc', '-static-libstdc++', 'audit.cpp', '-o', 'audit.exe'],
               cwd=WORK, env=env, check=True)
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
rng = random.Random(20260930)
sequences = []
for case in range(120):
    initial = rng.uniform(21, 99)
    samples = []
    for k in range(100):
        # These values include charging, temperature/reserve overrides, recovery
        # and low-runtime persistence, without intentionally indistinguishable
        # float-vs-double threshold crossings.
        current = (-rng.uniform(.05, 1.8) if case % 5 == 0 else rng.uniform(.05, 1.8))
        temperature = 46 if case % 7 == 0 and 20 <= k < 30 else 28
        voltage = 11.5 if case % 11 == 0 and 40 <= k < 50 else 13
        load = (10 if k < 55 else 2) if case % 3 == 0 else rng.uniform(3, 18)
        dt = (.1, .25, 1)[case % 3]
        samples.append(tuple(map(f32, [dt, voltage, current, load, temperature, 3])))
    sequences.append((initial, samples))
payload = [str(len(sequences))]
expected = []
for initial, samples in sequences:
    payload.append(f'{initial:.17g} {len(samples)}')
    c = Controller()
    c.synchronize(initial)
    c.optional_on = True
    for dt, voltage, current, load, temp, minimum in samples:
        payload.append(' '.join(format(x, '.17g') for x in (dt, voltage, current, load, temp, minimum)))
        expected.append(c.update(dt, voltage, current, load, temp, minimum_runtime_h=minimum))
ran = subprocess.run([str(WORK/'audit.exe')], input='\n'.join(payload)+'\n',
                     cwd=WORK, env=env, capture_output=True, text=True, check=True)
lines = ran.stdout.splitlines()
assert len(lines) == len(expected)
max_errors = {key: 0 for key in ('soc_pct', 'usable_energy_wh', 'runtime_h', 'runtime_no_solar_h')}
states = set()
for index, (line, row) in enumerate(zip(lines, expected)):
    fields = line.split()
    for key, value in zip(max_errors, fields[:4]):
        actual = float(value)
        wanted = row[key]
        if wanted is None:
            assert not math.isfinite(actual), (index, key, actual, wanted)
        else:
            error = abs(actual - wanted)
            max_errors[key] = max(max_errors[key], error)
            assert error < (1e-4 if key == 'soc_pct' else 1e-3), (index, key, actual, wanted)
    assert bool(int(fields[4])) == row['optional_on'], (index, fields, row)
    assert fields[5] == row['state'], (index, fields, row)
    states.add(row['state'])
after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (production/'controller.h', production/'config.h')}
assert before == after
report = {'status': 'PASS', 'seed': 20260930, 'sequences': len(sequences),
          'sample_comparisons': len(expected), 'policy_state_and_output_matches': len(expected),
          'maximum_absolute_numeric_errors': max_errors, 'observed_states': sorted(states),
          'production_files_unchanged': before == after, 'production_sha256': after,
          'scope': 'Host-compiled C++ isolated armed copy versus Python reference; healthy varied inputs only. '
                   'No ESP32 execution, GPIO, actual sensors, BMS or converter model coupling.'}
(OUT/'policy-differential.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
