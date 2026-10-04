"""Fit calibration candidates from independently paired instrument readings.

No serial commands or firmware writes. Current uses corrected = raw*gain-offset,
matching config.h. Battery voltage supports gain only, matching the firmware.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

CHANNELS = {
    'battery_current': ('A', 'BATTERY_CURRENT_GAIN', 'BATTERY_CURRENT_OFFSET_A'),
    'load_current': ('A', 'LOAD_CURRENT_GAIN', 'LOAD_CURRENT_OFFSET_A'),
    'solar_current': ('A', 'SOLAR_CURRENT_GAIN', 'SOLAR_CURRENT_OFFSET_A'),
    'battery_voltage': ('V', 'BATTERY_VOLTAGE_GAIN', None),
}

def calibrate(rows, allow_simulated=False):
    groups = {}
    sources = set()
    for line, row in enumerate(rows, start=2):
        channel = row.get('channel')
        if channel not in CHANNELS:
            raise ValueError(f'Row {line}: unknown channel {channel!r}.')
        if row.get('role') not in ('fit', 'validation'):
            raise ValueError(f'Row {line}: role must be fit or validation.')
        source = row.get('source_mode')
        if source not in ('hardware', 'simulated') or (source == 'simulated' and not allow_simulated):
            raise ValueError(f'Row {line}: physical calibration needs hardware data; simulated examples require --allow-simulated.')
        sources.add(source)
        if row.get('unit') != CHANNELS[channel][0]:
            raise ValueError(f'Row {line}: wrong unit for {channel}.')
        try:
            raw, reference = float(row['raw']), float(row['reference'])
        except (KeyError, ValueError, TypeError):
            raise ValueError(f'Row {line}: enter both raw and independent reference measurements.') from None
        if not math.isfinite(raw) or not math.isfinite(reference):
            raise ValueError(f'Row {line}: measurements must be finite.')
        if channel == 'battery_voltage':
            valid = 8 <= raw <= 16 and 8 <= reference <= 16
        else:
            valid = abs(raw) <= 2.1 and abs(reference) <= 2
            if channel != 'battery_current':
                valid = valid and raw >= -.05 and reference >= 0
        if not valid:
            raise ValueError(f'Row {line}: values outside this prototype calibration range.')
        groups.setdefault(channel, []).append(dict(raw=raw, reference=reference, role=row['role']))
    if not groups or len(sources) != 1:
        raise ValueError('Provide measurements with one consistent source_mode; never mix hardware and simulation.')
    report = {'source_mode': sources.pop(), 'method': 'independent fit and holdout validation', 'channels': {},
              'firmware_modified': False, 'physical_validation_claimed_by_tool': False}
    for name, samples in groups.items():
        fitted = [r for r in samples if r['role'] == 'fit']
        validation = [r for r in samples if r['role'] == 'validation']
        if len(fitted) < 3 or len(validation) < 2:
            raise ValueError(f'{name}: require at least three fit and two separate validation readings.')
        if len({r['raw'] for r in fitted}) < 3:
            raise ValueError(f'{name}: need three distinct fit inputs, not repeated copies of one point.')
        if len({r['raw'] for r in validation}) < 2 or len({r['reference'] for r in validation}) < 2:
            raise ValueError(f'{name}: validate at two distinct settings, not repeated copies of one point.')
        span = max(r['reference'] for r in fitted)-min(r['reference'] for r in fitted)
        if span < (1 if name == 'battery_voltage' else .2):
            raise ValueError(f'{name}: fit range is too narrow.')
        if name != 'battery_voltage' and not any(abs(r['reference']) <= .01 for r in fitted):
            raise ValueError(f'{name}: include a zero-current fit reading to establish offset.')
        if name == 'battery_voltage':
            gain = sum(r['raw']*r['reference'] for r in fitted)/sum(r['raw']**2 for r in fitted)
            offset = 0.0
        else:
            mx = sum(r['raw'] for r in fitted)/len(fitted)
            my = sum(r['reference'] for r in fitted)/len(fitted)
            gain = sum((r['raw']-mx)*(r['reference']-my) for r in fitted)/sum((r['raw']-mx)**2 for r in fitted)
            offset = gain*mx-my
        checks = []
        for r in samples:
            corrected = gain*r['raw']-offset
            limit = .01*abs(r['reference']) if name == 'battery_voltage' else .03*abs(r['reference'])+.01
            error = corrected-r['reference']
            checks.append({**r, 'corrected': corrected, 'error': error, 'allowed_error': limit, 'within_target': abs(error)<=limit+1e-12})
        reasonable = .8 <= gain <= 1.2 and (name == 'battery_voltage' or abs(offset) <= .05)
        passed = reasonable and all(r['within_target'] for r in checks)
        warnings = []
        if not reasonable:
            warnings.append('Large gain/offset correction: check shunt, range, polarity, wiring and reference instrument before use.')
        if name == 'battery_current' and not (min(r['reference'] for r in validation)<0<max(r['reference'] for r in validation)):
            warnings.append('Both charging and discharging directions have not been independently validated.')
        constants = {CHANNELS[name][1]: gain}
        if CHANNELS[name][2]: constants[CHANNELS[name][2]] = offset
        report['channels'][name] = {'status': 'CANDIDATE_PASS' if passed else 'REQUIRES_REVIEW',
            'unit': CHANNELS[name][0], 'gain': gain, 'offset': offset,
            'fit_reference_range': [min(r['reference'] for r in fitted), max(r['reference'] for r in fitted)],
            'constants': constants, 'warnings': warnings, 'readings': checks,
            'validation_max_abs_error': max(abs(r['error']) for r in checks if r['role']=='validation')}
    report['status'] = 'CANDIDATE_PASS' if all(c['status']=='CANDIDATE_PASS' for c in report['channels'].values()) else 'REQUIRES_REVIEW'
    if report['source_mode'] == 'simulated': report['notice'] = 'SIMULATED EXAMPLE ONLY. Do not use these values to calibrate hardware.'
    else: report['notice'] = 'Candidate constants from user-labelled hardware readings. Accuracy, instrument provenance and safe operating limits require independent review.'
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path); parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--allow-simulated',action='store_true')
    args=parser.parse_args()
    if args.input.resolve()==args.output.resolve():
        parser.error('Output must differ from the measurements file; raw measurements must be preserved.')
    try:
        payload=args.input.read_bytes()
        report=calibrate(list(csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))),args.allow_simulated)
    except (OSError,ValueError) as exc: parser.error(str(exc))
    report['input_file']=str(args.input.resolve())
    report['input_sha256']=hashlib.sha256(payload).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['notice'])
    for name, result in report['channels'].items():
        print(name+': '+result['status'])
        print('  '+', '.join(f'{key} = {value:.9g}' for key,value in result['constants'].items()))
        for warning in result['warnings']: print('  '+warning)
    print('Report: '+str(args.output))
    return 0 if report['status']=='CANDIDATE_PASS' else 2

if __name__=='__main__': raise SystemExit(main())
