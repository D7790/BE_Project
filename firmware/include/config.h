#pragma once
#include <stdint.h>

// REFERENCE CONFIGURATION ONLY. Confirm exact modules, supply rails, protection,
// calibration and active-high driver behavior before enabling physical control.
constexpr bool HARDWARE_CONFIRMED = false;
constexpr bool SOLAR_SENSOR_FITTED = false;
constexpr uint8_t PIN_SDA = 21;
constexpr uint8_t PIN_SCL = 22;
constexpr uint8_t PIN_OPTIONAL_ENABLE = 25;
constexpr uint8_t PIN_TEMPERATURE = 4;
constexpr uint8_t PIN_LOAD_BUTTON = 27;  // momentary switch to protected system GND
constexpr uint8_t PIN_SYNC_BUTTON = 26;  // hold 5 s AFTER a verified full-charge procedure
constexpr uint8_t BATTERY_SENSOR_ADDRESS = 0x40;
constexpr uint8_t LOAD_SENSOR_ADDRESS = 0x41;
constexpr uint8_t SOLAR_SENSOR_ADDRESS = 0x44;

// Reference sensors: INA219 with 0.1-ohm shunt, 32V/2A library calibration.
// Limits below are provisional project limits, not battery certification limits.
// Full charge to the pack manufacturer's normal discharge endpoint, before
// subtracting RESERVE_PCT. Do not enter only the Ah delivered to our 20% reserve.
constexpr float CAPACITY_AH = 6.0f;       // provisional until independently established
constexpr float NOMINAL_V = 12.8f;
constexpr float RESERVE_PCT = 20.0f;
constexpr float MINIMUM_RUNTIME_H = 3.0f;
constexpr float CHARGE_EFFICIENCY = 0.98f;
constexpr float MAX_PATH_CURRENT_A = 2.0f;
constexpr float LOW_OPERATING_V = 11.6f;
constexpr float HIGH_OPERATING_V = 14.7f;
constexpr float MAX_SURFACE_TEMPERATURE_C = 45.0f;
constexpr float OPTIONAL_INPUT_POWER_W = 3.5f;  // provisional; replace with measured upstream increment incl. loss
constexpr float RESTORE_MARGIN_H = 0.25f;
constexpr float SHED_DELAY_S = 3.0f;

// I_corrected = I_raw * gain - offset. Calibrate sign and offset for each channel.
constexpr float BATTERY_CURRENT_GAIN = 1.0f;
constexpr float BATTERY_CURRENT_OFFSET_A = 0.0f;
constexpr float LOAD_CURRENT_GAIN = 1.0f;
constexpr float LOAD_CURRENT_OFFSET_A = 0.0f;
constexpr float SOLAR_CURRENT_GAIN = 1.0f;
constexpr float SOLAR_CURRENT_OFFSET_A = 0.0f;
constexpr float BATTERY_VOLTAGE_GAIN = 1.0f;
