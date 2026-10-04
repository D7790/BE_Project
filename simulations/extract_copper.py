"""Read-only extraction of selected front-copper paths using KiCad Python.

R = rho L / (width * thickness). Ground pours/planes and pad spreading are
omitted. These are resistances of available paths, not a thermal/ampacity model.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import heapq
import json
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'hardware/pcb/wattsense-main-revB-4layer'
SOURCE = CAD / 'wattsense-main.kicad_pcb'
audit = json.loads((CAD / 'reports/power-path-audit.json').read_text())
assert audit['status'] == 'PASS'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == audit['pcb_sha256']
board = pcb.LoadBoard(str(SOURCE))
rho = 1.724e-8  # assumed bulk copper resistivity at 20 C, ohm m
alpha = .00393  # assumed linear temperature coefficient per C


def pad(name):
    ref, number = name.split('.')
    return board.FindFootprintByReference(ref).FindPadByNumber(number)


def point(v):
    return v.x, v.y


def path(first, last):
    a, b = pad(first), pad(last)
    assert a.GetNetCode() == b.GetNetCode()
    graph = defaultdict(list)
    for track in board.GetTracks():
        if isinstance(track, pcb.PCB_VIA) or track.GetLayer() != pcb.F_Cu:
            continue
        if track.GetNetCode() != a.GetNetCode():
            continue
        length, width = pcb.ToMM(track.GetLength()), pcb.ToMM(track.GetWidth())
        resistance = rho * length / width / 35e-6
        x, y = point(track.GetStart()), point(track.GetEnd())
        graph[x].append((y, resistance, length, width))
        graph[y].append((x, resistance, length, width))
    start, end = point(a.GetPosition()), point(b.GetPosition())
    queue = [(0., start, 0., float('inf'))]
    distances = {start: 0.}
    while queue:
        resistance, node, length, width = heapq.heappop(queue)
        if resistance > distances[node]:
            continue
        if node == end:
            return {'from': first, 'to': last, 'net': a.GetNetname(),
                    'length_mm': length, 'minimum_width_mm': width,
                    'R_35um_20C_ohm': resistance,
                    'R_25um_60C_ohm': resistance * 35 / 25 * (1 + alpha * 40)}
        for nxt, r, segment, w in graph[node]:
            candidate = resistance + r
            if candidate < distances.get(nxt, float('inf')):
                distances[nxt] = candidate
                heapq.heappush(queue, (candidate, nxt, length + segment, min(width, w)))
    raise AssertionError(f'No explicit front-copper path: {first} -> {last}')


paths = {f"{item['from']}--{item['to']}": path(item['from'], item['to'])
         for item in audit['paths']}
groups = {
    'hv_loop': ['J1.1--R1.1', 'R1.2--R3.2', 'R3.2--R2.1', 'R2.2--J3.1',
                'J1.2--J2.2', 'J2.2--J3.2'],
    'output_common': ['J4.1--F1.1', 'F1.2--F2.1', 'J4.2--J5.2'],
    'lamp_branch': ['F2.2--J5.1'],
    'fan_branch': ['F2.1--F3.1', 'F3.2--J6.1', 'J6.2--D1.2',
                   'D1.2--Q1.3', 'J5.2--Q1.2'],
}
result = {
    'scope': 'Selected explicit F.Cu paths only. Lumped branch model, no pours, '
             'pad spreading, contacts, vias, inductance or self-heating solver. '
             '35 um/20 C reference and 25 um/60 C sensitivity are assumptions, '
             'not as-fabricated thickness or predicted temperature.',
    'pcb_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'rho_20C_ohm_m': rho, 'alpha_per_C': alpha, 'paths': paths,
    'group_members': groups,
    'groups': {name: {key: sum(paths[p][key] for p in members)
                      for key in ['R_35um_20C_ohm', 'R_25um_60C_ohm']}
               for name, members in groups.items()},
}
(ROOT / 'simulations/results/copper-resistance.json').write_text(json.dumps(result, indent=2))
print('Extracted 20 copper paths without modifying CAD.')
