import unittest
from simulations.hardware_model import battery_point, interpolate_ocv, output_network, source_current


class HardwareModelTests(unittest.TestCase):
    def test_ideal_source_and_zero_load(self):
        self.assertEqual(source_current(12.8, 0, 6.4), .5)
        self.assertEqual(source_current(12.8, .3, 0), 0)

    def test_constant_power_matches_kirchhoff(self):
        for e in [11.6, 12.8, 14.6]:
            for r in [.05, .2, .5]:
                for p in [2, 8, 15]:
                    i = source_current(e, r, p)
                    self.assertAlmostEqual((e - i * r) * i, p, places=11)

    def test_impossible_source_and_invalid_inputs_rejected(self):
        for args in [(5, 1, 10), (0, .1, 1), (5, -.1, 1), (5, .1, -1), (float('nan'), 0, 1)]:
            with self.assertRaises(ValueError):
                source_current(*args)

    def test_network_ideal_limit(self):
        n = output_network(3, 3, .8, 0, 0, 0)
        self.assertAlmostEqual(n['output_a'], 1.36)
        self.assertEqual(n['fan_v'], 5)

    def test_network_conservation_and_fan_off(self):
        for fan in [0, 2.5, 3]:
            n = output_network(3, fan, .8, .12, .15, .19)
            self.assertAlmostEqual(n['energy_balance_error_w'], 0, places=10)
            self.assertGreater(n['converter_output_w'], n['delivered_w'])
            self.assertLess(n['lamp_v'], 5)
            if fan == 0:
                self.assertEqual(n['fan_a'], 0)

    def test_lower_efficiency_increases_battery_demand(self):
        good = battery_point(13, 7, .95, .1, .08, .03)
        bad = battery_point(13, 7, .8, .1, .08, .03)
        self.assertGreater(bad['battery_a'], good['battery_a'])
        self.assertGreater(bad['converter_loss_w'], good['converter_loss_w'])

    def test_battery_power_conservation(self):
        for eff in [.8, .9, .95, 1.]:
            n = battery_point(13, 7, eff, .1, .08, .03)
            self.assertAlmostEqual(n['energy_balance_error_w'], 0, places=11)
            losses = sum(n[k] for k in ['converter_loss_w', 'battery_internal_loss_w',
                                       'hv_wire_loss_w', 'hv_copper_loss_w', 'two_shunts_loss_w'])
            self.assertAlmostEqual(n['chemical_power_w'], 7 + losses, places=11)

    def test_ocv_interpolation_and_invalid_order(self):
        self.assertEqual(interpolate_ocv(50, [[20, 12.8], [80, 13.2]]), 13.)
        self.assertEqual(interpolate_ocv(10, [[20, 12.8], [80, 13.2]]), 12.8)
        with self.assertRaises(ValueError):
            interpolate_ocv(50, [[80, 13.2], [20, 12.8]])


if __name__ == '__main__':
    unittest.main()
