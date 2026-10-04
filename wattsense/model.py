"""Reference estimator and policy for the simulator. No hardware is controlled here."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Config:
    capacity_ah: float = 6.0
    nominal_voltage: float = 12.8
    reserve_pct: float = 20.0
    minimum_runtime_h: float = 3.0
    charge_efficiency: float = 0.98
    sustained_s: float = 3.0
    max_gap_s: float = 2.0
    low_operating_v: float = 11.6
    high_operating_v: float = 14.7

    def __post_init__(self):
        if not 0.1 <= self.capacity_ah <= 100:
            raise ValueError("capacity_ah must be between 0.1 and 100")
        if not 0 <= self.reserve_pct < 100:
            raise ValueError("reserve_pct must be between 0 and 100")
        if not 0 <= self.minimum_runtime_h <= 24:
            raise ValueError("minimum_runtime_h must be between 0 and 24")


class Controller:
    """Positive battery current means discharge. Reboots start unsynchronized."""
    def __init__(self, config=None):
        self.config = config or Config()
        self.soc_pct = None
        self.optional_on = False
        self.state = "UNCALIBRATED"
        self.reason = "Battery charge reference has not been established."
        self.below_for = 0.0
        self.filtered_discharge_w = None
        self.policy_shed = False

    def synchronize(self, reference_pct):
        if not math.isfinite(reference_pct) or not 0 <= reference_pct <= 100:
            raise ValueError("Reference charge must be a finite percentage.")
        self.soc_pct = float(reference_pct)
        self.below_for = 0
        self.filtered_discharge_w = None

    def update(self, dt_s, voltage_v, battery_current_a, load_w,
               temperature_c, sensor_ok=True, requested=True,
               automatic=True, minimum_runtime_h=None):
        cfg = self.config
        minimum = cfg.minimum_runtime_h if minimum_runtime_h is None else minimum_runtime_h
        values = (dt_s, voltage_v, battery_current_a, load_w, temperature_c, minimum)
        valid = (all(isinstance(x, (int, float)) and not isinstance(x, bool)
                     and math.isfinite(x) for x in values)
                 and 0 < dt_s <= cfg.max_gap_s and 8 <= voltage_v <= 16
                 and abs(battery_current_a) <= 2.0 and 0 <= load_w <= 35
                 and -10 <= temperature_c <= 70 and 0 <= minimum <= 24
                 and sensor_ok)
        if not valid:
            self.soc_pct = None
            self.optional_on = False
            self.below_for = 0
            self.filtered_discharge_w = None
            self.policy_shed = False
            self.state, self.reason = "SENSOR_FAULT", "Missing, invalid or interrupted measurement; optional load off."
            return self.result(None, None, None)
        if self.soc_pct is None:
            self.optional_on = False
            self.state, self.reason = "UNCALIBRATED", "Synchronize charge after establishing a battery reference."
            return self.result(None, None, None)
        effective_a = battery_current_a * (cfg.charge_efficiency if battery_current_a < 0 else 1)
        self.soc_pct = min(100.0, max(0.0, self.soc_pct -
                           100 * effective_a * dt_s / (3600 * cfg.capacity_ah)))
        discharge_w = voltage_v * battery_current_a
        alpha = 1 - math.exp(-dt_s / 3.0)
        self.filtered_discharge_w = (discharge_w if self.filtered_discharge_w is None else
                                    self.filtered_discharge_w + alpha *
                                    (discharge_w - self.filtered_discharge_w))
        energy = max(0.0, self.soc_pct - cfg.reserve_pct) / 100 * cfg.capacity_ah * cfg.nominal_voltage
        runtime = energy / self.filtered_discharge_w if self.filtered_discharge_w > 0.2 else None
        no_solar = energy / load_w if load_w > 0.2 else None
        if temperature_c >= 45:
            self.optional_on = False
            self.below_for = 0
            self.state, self.reason = "TEMPERATURE", "Surface temperature reached the provisional 45 °C limit."
        elif voltage_v <= cfg.low_operating_v or voltage_v > cfg.high_operating_v or self.soc_pct <= cfg.reserve_pct:
            self.optional_on = False
            self.below_for = 0
            self.state, self.reason = "RESERVE", "Configured voltage or charge operating limit reached."
        elif not requested:
            self.optional_on = False
            self.policy_shed = False
            self.below_for = 0
            self.state, self.reason = "MANUAL_OFF", "Optional load disabled by the operator."
        elif automatic and no_solar is not None and no_solar < minimum:
            self.below_for += dt_s
            if self.below_for + 1e-9 >= cfg.sustained_s:
                self.optional_on = False
                self.policy_shed = True
                self.state, self.reason = "PRIORITY", "Backup-time requirement exceeded; optional load shed."
            else:
                self.state, self.reason = "WATCH", "Checking sustained backup-time condition."
        else:
            self.below_for = 0
            self.state = "NORMAL" if self.optional_on else "PRIORITY" if self.policy_shed else "RECOVERY"
            self.reason = ("Loads within the configured operating policy." if self.optional_on else
                           "Backup policy shed the optional load; request restoration when sufficient margin returns."
                           if self.policy_shed else "Optional load stays off until an explicit restore request.")
        return self.result(energy, runtime, no_solar)

    def result(self, energy, runtime, no_solar):
        return {
            "soc_pct": self.soc_pct, "usable_energy_wh": energy,
            "runtime_h": runtime, "runtime_no_solar_h": no_solar,
            "optional_on": self.optional_on, "state": self.state, "reason": self.reason,
            "estimate_valid": self.soc_pct is not None,
        }

    def request_restore(self, prospective_load_w, minimum_runtime_h, temperature_c=28, voltage_v=12.8):
        """Check expected consumption with the load ON; never use the off-load runtime."""
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
                   for x in (prospective_load_w, minimum_runtime_h, temperature_c, voltage_v)):
            return False
        if not 0 <= minimum_runtime_h <= 24 or not -10 <= temperature_c < 45:
            return False
        if not self.config.low_operating_v < voltage_v <= self.config.high_operating_v:
            return False
        if self.soc_pct is None or temperature_c >= 45 or self.soc_pct <= self.config.reserve_pct:
            return False
        if not 0 < prospective_load_w <= 35:
            return False
        energy = (self.soc_pct - self.config.reserve_pct) / 100 * self.config.capacity_ah * self.config.nominal_voltage
        if energy / prospective_load_w < minimum_runtime_h + 0.25:
            return False
        self.optional_on = True
        self.policy_shed = False
        self.below_for = 0
        return True
