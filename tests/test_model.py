import unittest
from wattsense.model import Controller, Config
from wattsense.simulator import Simulator


class EstimatorTests(unittest.TestCase):
    def test_unknown_at_boot_and_after_invalid_measurement(self):
        controller = Controller()
        result = controller.update(1, 13, 1, 13, 28)
        self.assertIsNone(result["soc_pct"])
        self.assertFalse(result["optional_on"])
        controller.synchronize(80)
        result = controller.update(1, 13, float("nan"), 13, 28)
        self.assertEqual(result["state"], "SENSOR_FAULT")
        self.assertIsNone(controller.soc_pct)
        self.assertEqual(controller.update(1, 13, 1, 13, 28)["state"], "UNCALIBRATED")

    def test_known_charge_balance_and_sign(self):
        controller = Controller()
        controller.synchronize(80)
        for _ in range(3600):
            controller.update(1, 12.8, 1, 12.8, 28, requested=False)
        self.assertAlmostEqual(controller.soc_pct, 80 - 100 / 6, places=7)
        for _ in range(3600):
            controller.update(1, 12.8, -1, 0, 28, requested=False)
        self.assertAlmostEqual(controller.soc_pct, 80 - 100 / 6 + 100 * .98 / 6, places=7)

    def test_gap_requires_new_reference(self):
        controller = Controller()
        controller.synchronize(80)
        self.assertFalse(controller.update(10, 13, 1, 13, 28)["estimate_valid"])

    def test_runtime_includes_reserve(self):
        controller = Controller()
        controller.synchronize(60)
        result = controller.update(1, 12.8, .5, 6.4, 28)
        expected = (controller.soc_pct - 20) / 100 * 6 * 12.8 / 6.4
        self.assertAlmostEqual(result["runtime_no_solar_h"], expected)

    def test_sustained_shedding_not_single_transient(self):
        controller = Controller()
        controller.synchronize(30)
        controller.optional_on = True
        for _ in range(2):
            self.assertTrue(controller.update(1, 13, 1, 13, 28)["optional_on"])
        self.assertFalse(controller.update(1, 13, 1, 13, 28)["optional_on"])

    def test_restore_checks_full_load_and_keeps_latched_off(self):
        controller = Controller()
        controller.synchronize(40)
        controller.optional_on = False
        controller.update(1, 13, .1, 1.3, 28)
        self.assertFalse(controller.optional_on)
        self.assertFalse(controller.request_restore(10, 3))
        self.assertTrue(controller.request_restore(4, 3))

    def test_shed_reason_survives_the_resulting_lower_load(self):
        controller = Controller()
        controller.synchronize(68)
        controller.optional_on = True
        for _ in range(3):
            controller.update(1, 13, .6, 7.8, 28, minimum_runtime_h=6)
        result = controller.update(1, 13, .3, 3.9, 28, minimum_runtime_h=6)
        self.assertFalse(result["optional_on"])
        self.assertEqual(result["state"], "PRIORITY")

    def test_charging_never_has_negative_runtime(self):
        controller = Controller()
        controller.synchronize(60)
        result = controller.update(1, 13, -.5, 4, 28)
        self.assertIsNone(result["runtime_h"])
        self.assertGreater(result["runtime_no_solar_h"], 0)

    def test_temperature_and_reserve_override_requests(self):
        controller = Controller()
        controller.synchronize(80)
        controller.optional_on = True
        self.assertFalse(controller.update(1, 13, 1, 13, 46)["optional_on"])
        self.assertFalse(controller.request_restore(4, 3, 46))
        controller.synchronize(19)
        self.assertEqual(controller.update(1, 13, 1, 13, 28)["state"], "RESERVE")

    def test_simulator_scenarios_and_fault(self):
        sim = Simulator()
        sim.command({"action": "scenario", "value": "reserve"})
        for _ in range(40):
            row = sim.step(.1)
        self.assertFalse(row["optional_on"])
        self.assertEqual(row["source_mode"], "simulated")
        sim.command({"action": "scenario", "value": "solar"})
        self.assertLess(sim.step()["battery_a"], 0)
        sim.command({"action": "fault", "value": True})
        self.assertIsNone(sim.step()["soc_pct"])
        sim.command({"action": "fault", "value": False})
        self.assertFalse(sim.step()["estimate_valid"])

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            Config(capacity_ah=0)
        for value in [float("nan"), 120, -1]:
            with self.assertRaises(ValueError):
                Controller().synchronize(value)
        with self.assertRaises(ValueError):
            Simulator().command({"action": "minimum_runtime", "value": True})


if __name__ == "__main__":
    unittest.main()
