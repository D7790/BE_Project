import unittest
import subprocess
import sys
import tempfile
from pathlib import Path
from wattsense.calibration import calibrate

def points(channel='battery_current',source='hardware',gain=1.02,offset=.008):
    vals=[(-.8,'fit'),(0,'fit'),(.8,'fit'),(-.4,'validation'),(.4,'validation')]
    return [dict(channel=channel,role=role,raw=str((ref+offset)/gain),reference=str(ref),unit='A',source_mode=source) for ref,role in vals]

class CalibrationTests(unittest.TestCase):
    def test_repeated_validation_point_is_not_range_validation(self):
        rows=points(); rows[-1]=dict(rows[-2])
        with self.assertRaises(ValueError):calibrate(rows)

    def test_cli_cannot_overwrite_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'measurements.csv'
            original=b'raw measurements must survive\n';path.write_bytes(original)
            result=subprocess.run([sys.executable,'-m','wattsense.calibration',str(path),'--output',str(path)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Output must differ',result.stderr)
            self.assertEqual(path.read_bytes(),original)

    def test_fit_matches_firmware_offset_sign(self):
        r=calibrate(points())['channels']['battery_current']
        self.assertEqual(r['status'],'CANDIDATE_PASS')
        self.assertAlmostEqual(r['gain'],1.02); self.assertAlmostEqual(r['offset'],.008)
        self.assertFalse(r['warnings'])

    def test_voltage_gain_only(self):
        rows=[dict(channel='battery_voltage',role='fit' if i<3 else 'validation',raw=v/1.01,reference=v,unit='V',source_mode='hardware') for i,v in enumerate([11.8,13,14.6,12.4,13.8])]
        r=calibrate(rows)['channels']['battery_voltage']
        self.assertAlmostEqual(r['gain'],1.01); self.assertEqual(r['offset'],0)
        self.assertEqual(list(r['constants']),['BATTERY_VOLTAGE_GAIN'])

    def test_holdout_failure_is_not_hidden_by_fit(self):
        rows=points();rows[-1]['reference']='.48'
        self.assertEqual(calibrate(rows)['status'],'REQUIRES_REVIEW')

    def test_simulation_requires_explicit_opt_in_and_label(self):
        with self.assertRaises(ValueError): calibrate(points(source='simulated'))
        r=calibrate(points(source='simulated'),True)
        self.assertEqual(r['source_mode'],'simulated'); self.assertIn('SIMULATED',r['notice'])
        rows=points(); rows[0]['source_mode']='simulated'
        with self.assertRaises(ValueError):calibrate(rows,True)

    def test_rejects_missing_degenerate_and_nonfinite_measurements(self):
        for field,value in [('raw',''),('raw','nan'),('reference','inf'),('unit','mA'),('role','test')]:
            rows=points();rows[1][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):calibrate(rows)
        with self.assertRaises(ValueError):calibrate(points()[:3])
        rows=points()
        for row in rows:row['raw']='.1'
        with self.assertRaises(ValueError):calibrate(rows)

    def test_polarity_error_is_review_required(self):
        rows=points(gain=-1)
        self.assertEqual(calibrate(rows)['status'],'REQUIRES_REVIEW')

    def test_current_fit_requires_zero(self):
        rows=points();rows[1]['reference']='.1'
        with self.assertRaises(ValueError):calibrate(rows)
