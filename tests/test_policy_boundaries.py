import math
import unittest
from wattsense.model import Controller

class BoundaryTests(unittest.TestCase):
    def ready(self):
        c=Controller(); c.synchronize(80); c.optional_on=True; return c

    def test_voltage_operating_limits_override_optional_load(self):
        for voltage in [11.6,11.0,14.71,15.5]:
            with self.subTest(voltage=voltage):
                c=self.ready(); r=c.update(.1,voltage,.5,6,28)
                self.assertEqual(r['state'],'RESERVE'); self.assertFalse(r['optional_on'])
                self.assertFalse(c.request_restore(6,3,28,voltage))

    def test_restore_rejects_nonfinite_and_out_of_range_arguments(self):
        for args in [(6,math.nan,28,13),(6,3,math.nan,13),(6,3,28,math.nan),
                     (6,-1,28,13),(6,25,28,13),(6,3,-11,13),(36,3,28,13),
                     (True,3,28,13),(6,3,28,11.6)]:
            with self.subTest(args=args):
                c=self.ready(); c.optional_on=False
                self.assertFalse(c.request_restore(*args)); self.assertFalse(c.optional_on)

    def test_thermal_interruption_resets_sustained_timer(self):
        c=self.ready()
        for _ in range(2): c.update(1,13,.5,7,28,minimum_runtime_h=10)
        self.assertEqual(c.state,'WATCH')
        c.update(.1,13,.5,7,46,minimum_runtime_h=10)
        c.update(1,13,.5,7,28,minimum_runtime_h=10)
        self.assertEqual(c.state,'WATCH'); self.assertFalse(c.policy_shed)

    def test_current_limit_is_consistent_with_firmware(self):
        for current in [-2.01,2.01]:
            c=self.ready(); r=c.update(.1,13,current,7,28)
            self.assertEqual(r['state'],'SENSOR_FAULT'); self.assertIsNone(r['soc_pct'])

    def test_fault_recovery_needs_reference_and_explicit_restore(self):
        c=self.ready(); c.update(.1,13,.5,7,28,sensor_ok=False)
        self.assertFalse(c.request_restore(7,3))
        self.assertEqual(c.update(.1,13,.5,7,28)['state'],'UNCALIBRATED')
        c.synchronize(80)
        self.assertFalse(c.update(.1,13,.5,7,28)['optional_on'])
        self.assertTrue(c.request_restore(7,3))
