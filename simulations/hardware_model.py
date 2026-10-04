"""Lumped electrical plant. All parameters are assumptions until measured."""
import math


def positive(value, name, allow_zero=False):
    if not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f'Invalid {name}')


def source_current(voltage, resistance, power):
    """Stable, low-current solution of P = I (E - I R)."""
    positive(voltage, 'voltage')
    positive(resistance, 'resistance', True)
    positive(power, 'power', True)
    discriminant = voltage * voltage - 4 * resistance * power
    if discriminant <= 0:
        raise ValueError('No stable constant-power operating point')
    return 2 * power / (voltage + math.sqrt(discriminant))


def interpolate_ocv(soc, points):
    """Illustrative piecewise OCV, not a measured LiFePO4 discharge curve."""
    if not math.isfinite(soc) or not points or not 0 <= soc <= 100:
        raise ValueError('Invalid state of charge')
    if any(b[0] <= a[0] for a, b in zip(points, points[1:])):
        raise ValueError('OCV points must be strictly ordered')
    if soc <= points[0][0]:
        return points[0][1]
    for (s0, v0), (s1, v1) in zip(points, points[1:]):
        if soc <= s1:
            return v0 + (v1 - v0) * (soc - s0) / (s1 - s0)
    return points[-1][1]


def output_network(lamp_w, fan_w, controller_w, common_r, lamp_r, fan_r, supply_v=5.):
    """Constant delivered load powers, series losses, regulated 5 V at J4.

    Uses the high-voltage branch of each constant-power load. The controller is
    placed at the common rail; its entire 5 V demand includes sensors/3.3 V loss.
    This is not a model of the actual fan's electronics or ESP32 regulator.
    """
    for value in [lamp_w, fan_w, controller_w, common_r, lamp_r, fan_r]:
        positive(value, 'load/resistance', True)
    positive(supply_v, 'supply_v')
    rail = supply_v
    for _ in range(100):
        lamp_i = source_current(rail, lamp_r, lamp_w)
        fan_i = source_current(rail, fan_r, fan_w)
        controller_i = controller_w / rail
        total = lamp_i + fan_i + controller_i
        new_rail = supply_v - common_r * total
        if new_rail <= 0:
            raise ValueError('Collapsed 5 V rail')
        if abs(new_rail - rail) < 1e-12:
            rail = new_rail
            break
        rail = new_rail
    else:
        raise ValueError('No stable 5 V operating point')
    # Re-evaluate at the converged rail for independent power accounting.
    lamp_i = source_current(rail, lamp_r, lamp_w)
    fan_i = source_current(rail, fan_r, fan_w)
    controller_i = controller_w / rail
    total = lamp_i + fan_i + controller_i
    losses = total**2 * common_r + lamp_i**2 * lamp_r + fan_i**2 * fan_r
    return {'rail_v': rail, 'lamp_v': rail - lamp_i * lamp_r,
            'fan_v': rail - fan_i * fan_r, 'lamp_a': lamp_i, 'fan_a': fan_i,
            'controller_a': controller_i, 'output_a': total,
            'converter_output_w': supply_v * total, 'output_path_loss_w': losses,
            'delivered_w': lamp_w + fan_w + controller_w,
            'energy_balance_error_w': supply_v * total - losses - lamp_w - fan_w - controller_w}


def battery_point(ocv, converter_output_w, efficiency, battery_r, wire_r, copper_r, shunt_r=.1):
    if not 0 < efficiency <= 1:
        raise ValueError('Invalid converter efficiency')
    for value in [battery_r, wire_r, copper_r, shunt_r]:
        positive(value, 'resistance', True)
    input_w = converter_output_w / efficiency
    resistance = battery_r + wire_r + copper_r + 2 * shunt_r
    current = source_current(ocv, resistance, input_w)
    buck_v = ocv - current * resistance
    # Lumped sensing: U1 at battery-side copper, U2 immediately before R2.
    # Small distributed GND/sense-reference drops are not emulated here.
    battery_v = ocv - current * (battery_r + wire_r)
    load_w = (buck_v + current * shunt_r) * current
    return {'battery_a': current, 'battery_v': battery_v, 'buck_input_v': buck_v,
            'load_sensor_w': load_w, 'chemical_power_w': ocv * current,
            'converter_input_w': input_w,
            'converter_loss_w': input_w - converter_output_w,
            'battery_internal_loss_w': current**2 * battery_r,
            'hv_wire_loss_w': current**2 * wire_r,
            'hv_copper_loss_w': current**2 * copper_r,
            'two_shunts_loss_w': current**2 * 2 * shunt_r,
            'energy_balance_error_w': ocv * current - input_w - current**2 * resistance}
