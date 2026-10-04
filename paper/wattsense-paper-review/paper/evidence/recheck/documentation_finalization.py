"""Record scoped terminology corrections; preserve historical audit records."""
from pathlib import Path
import csv
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAD = ROOT / 'hardware/pcb/wattsense-main-revB-4layer'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = json.loads((HERE / 'documentation-before.json').read_text(encoding='utf-8-sig'))
changes = [{'path': str(Path(item['Path']).relative_to(ROOT)),
            'before_sha256': item['Hash'].lower(), 'after_sha256': digest(Path(item['Path']))}
           for item in before]
old = json.loads((ROOT / 'docs/evidence/final-audit-record.json').read_text())
sources_match = all(digest(ROOT / name) == expected for name, expected in old['source_sha256'].items())
cad_match = all(digest(CAD / name) == expected for name, expected in old['cad_native_sha256'].items())
archive_match = digest(CAD / 'exports/wattsense-main-revB-4layer-prototype.zip') == old['archive_sha256']
assert sources_match and cad_match and archive_match
summary = json.loads((ROOT / 'simulations/results/hardware-summary.json').read_text())
fields = ['case', 'assumed_start_current_at_5v_a', 'lamp_current_at_5v_a', 'fan_run_current_at_5v_a',
          'assumed_supply_limit_a', 'assumed_module_capacitance_uf', 'min_rail_v',
          'min_fan_terminal_v', 'peak_supply_a', 'rail_screening_floor_v', 'rail_screen']
with (HERE / 'startup-case-table.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows({key: row[key] for key in fields} for row in summary['startup_cases'])
ignored = []
for report in ['erc', 'drc']:
    obj = json.loads((HERE / (report + '.json')).read_text())
    ignored.extend({'report': report.upper(), **item} for item in obj['ignored_checks'])
with (HERE / 'ignored-cad-checks.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['report', 'key', 'description'])
    writer.writeheader()
    writer.writerows(ignored)

out = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS_DOCUMENTATION_ONLY_CORRECTIONS',
    'software_and_model_sources_match_28_Sep_checkpoint': sources_match,
    'native_CAD_matches_28_Sep_checkpoint': cad_match,
    'manufacturing_archive_matches_28_Sep_checkpoint': archive_match,
    'document_changes': changes,
    'earlier_recheck': 'publication-evidence-check.json is an accurate pre-correction snapshot. Documentation hashes intentionally differ now; no historical audit is overwritten.',
    'historical_final_audit_record_sha256': digest(ROOT / 'docs/evidence/final-audit-record.json'),
    'source_hardware_summary_sha256': digest(ROOT / 'simulations/results/hardware-summary.json'),
    'startup_cases': summary['startup_cases'],
    'ignored_cad_checks': ignored,
}
(HERE / 'documentation-finalization.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
lines = [
    'Documentation terminology corrections - 30 September 2026',
    '',
    'Corrected unjustified descriptions of no-future-solar runtime as conservative.',
    'The policy uses nominal remaining energy / measured load-branch power and omits',
    'some upstream losses. Excluding future charge does not make a guaranteed lower',
    'bound on runtime. It is now described as a no-future-charge heuristic estimate.',
    '',
    'Changed paths:',
]
for row in changes:
    lines.extend([row['path'], '  before SHA-256: ' + row['before_sha256'],
                  '  after SHA-256:  ' + row['after_sha256']])
lines.extend([
    '',
    'README: demo wording and limitations clarified.',
    'PROTOCOL: existing runtime_no_solar_h field documented accurately; API unchanged.',
    'REVIEW_DEMO: presentation language corrected to avoid a guaranteed minimum.',
    'firmware/README: behavior and MIN_H command description corrected; code unchanged.',
    'BLUEPRINT: distinguishes net runtime from the no-future-charge heuristic.',
    'PROJECT_FLOW: clarifies the same policy limitation in the end-to-end explanation.',
    '',
    'No API/internal variable, firmware, model, test, configuration or CAD changes.',
    'All recorded software/model and native CAD hashes still match 28 September.',
    'The manufacturing archive is unchanged. The September 28 audit remains historical.',
    'The earlier September 30 publication recheck records the pre-correction snapshot;',
    'documentation-finalization.json records this intentional subsequent change.',
    '',
    'Paper tables:',
    'paper/evidence/recheck/startup-case-table.csv contains six case IDs and outcomes.',
    'paper/evidence/recheck/ignored-cad-checks.csv lists four ERC and five DRC ignored categories.',
])
(ROOT / 'paper/evidence/documentation-corrections.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'status': out['status'], 'corrected_documents': len(changes),
                  'unchanged_software_model_sources': sources_match, 'unchanged_native_CAD': cad_match,
                  'startup_cases': len(summary['startup_cases']), 'ignored_categories': len(ignored)}))
