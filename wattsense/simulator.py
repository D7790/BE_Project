"""Deterministic illustrative plant. Output is never experimental evidence."""
import math
from .model import Controller


class Simulator:
    def __init__(self):
        self.elapsed = 0.0
        self.minimum_runtime_h = 3.0
        self.essential_w = 3.0
        self.optional_w = 3.0
        self.controller_w = 0.8
        self.converter_efficiency = 0.90
        self.temperature_c = 28.0
        self.solar_w = 0.0
        self.sensor_fault = False
        self.requested = True
        self.automatic = True
        self.controller = Controller()
        self.truth_soc = 68.0
        self.reset("normal")

    def load_w(self, optional):
        return (self.essential_w + (self.optional_w if optional else 0) +
                self.controller_w) / self.converter_efficiency

    def reset(self, scenario):
        scenarios = {"normal": (68, 0), "reserve": (27, 0),
                     "solar": (68, 10), "fault": (68, 0)}
        if not isinstance(scenario, str) or scenario not in scenarios:
            raise ValueError("Unknown scenario.")
        self.scenario_name = scenario
        self.truth_soc, self.solar_w = scenarios[scenario]
        self.sensor_fault = scenario == "fault"
        self.controller = Controller()
        self.controller.synchronize(self.truth_soc)
        self.controller.optional_on = True
        self.requested, self.automatic = True, True
        self.elapsed = 0

    def command(self, body):
        action = body.get("action")
        if action == "scenario":
            self.reset(body.get("value"))
            return "Loaded illustrative scenario: " + body["value"]
        if action == "minimum_runtime":
            value = body.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 12:
                raise ValueError("Runtime requirement must be between 0 and 12 hours.")
            self.minimum_runtime_h = float(value)
            return "Minimum backup-time requirement changed."
        if action == "optional_off":
            self.requested = False
            self.controller.optional_on = False
            return "Optional load switched off."
        if action == "restore":
            if self.sensor_fault:
                return "Restore refused: the sensor fault must be cleared first."
            voltage = 12.6 + 0.7 * self.truth_soc / 100
            restored = self.controller.request_restore(self.load_w(True), self.minimum_runtime_h, self.temperature_c, voltage)
            if restored:
                self.requested = True
            return "Optional load restored." if restored else "Restore refused: insufficient backup margin or invalid estimate."
        if action == "fault":
            if not isinstance(body.get("value"), bool):
                raise ValueError("Fault value must be true or false.")
            self.sensor_fault = body["value"]
            return "Simulated sensor fault changed. Reset a scenario to establish a new charge reference."
        raise ValueError("Unsupported simulator action.")

    def step(self, dt_s=0.1):
        self.elapsed += dt_s
        voltage = 12.6 + 0.7 * self.truth_soc / 100
        # Add deterministic ripple only to the illustrative measured load.
        load = self.load_w(self.controller.optional_on) + 0.025 * math.sin(self.elapsed)
        current = (load - self.solar_w) / voltage
        self.truth_soc = min(100, max(0, self.truth_soc -
                          current * (0.98 if current < 0 else 1) * dt_s / 216))
        measured = self.controller.update(
            dt_s, voltage, current, load, self.temperature_c,
            sensor_ok=not self.sensor_fault, requested=self.requested,
            automatic=self.automatic, minimum_runtime_h=self.minimum_runtime_h)
        return {
            "protocol": 1, "device_id": "SIMULATOR", "uptime_ms": round(self.elapsed * 1000),
            "source_mode": "simulated", "sensor_ok": not self.sensor_fault,
            "battery_v": None if self.sensor_fault else voltage,
            "battery_a": None if self.sensor_fault else current,
            "battery_w": None if self.sensor_fault else voltage * current,
            "load_w": None if self.sensor_fault else load,
            "solar_w": None if self.sensor_fault else self.solar_w,
            "temperature_c": None if self.sensor_fault else self.temperature_c,
            "minimum_runtime_h": self.minimum_runtime_h,
            "reserve_pct": self.controller.config.reserve_pct,
            "capacity_ah": self.controller.config.capacity_ah,
            "hardware_armed": False,
            **measured,
        }
