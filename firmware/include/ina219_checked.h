#pragma once
#include <stdint.h>
#include <math.h>

// Matches Adafruit INA219 1.2.3 setCalibration_32V_2A(), 0.1-ohm shunt.
// The 32 V register setting does NOT raise the IC's 26 V input rating.
constexpr uint16_t INA_EXPECTED_CONFIG = 0x399F;
constexpr uint16_t INA_EXPECTED_CALIBRATION = 4096;

struct Ina219Reading {
    float busV = NAN;       // IN- relative to GND
    float shuntV = NAN;     // IN+ minus IN-
    float currentA = NAN;   // uncorrected, signed current
};

inline int32_t signedRegister(uint16_t raw) {
    return raw < 0x8000 ? int32_t(raw) : int32_t(raw) - 65536;
}

// read(reg, value) must return false on any address, write or short-read error.
// Do not use a successful later transaction to hide an earlier read failure.
template <class Reader>
bool readIna219Checked(Reader read, Ina219Reading& output) {
    output = Ina219Reading();
    uint16_t config, calibration, bus, shunt, current, endConfig, endCalibration, endBus;
    if (!read(0x00, config) || !read(0x05, calibration) ||
        !read(0x02, bus) || !read(0x01, shunt) || !read(0x04, current) ||
        !read(0x02, endBus) || !read(0x00, endConfig) || !read(0x05, endCalibration))
        return false;
    if (config != INA_EXPECTED_CONFIG || endConfig != INA_EXPECTED_CONFIG ||
        calibration != INA_EXPECTED_CALIBRATION || endCalibration != INA_EXPECTED_CALIBRATION ||
        (bus & 1) || (endBus & 1)) return false;
    output.busV = (bus >> 3) * .004f;
    output.shuntV = signedRegister(shunt) * .00001f;
    output.currentA = signedRegister(current) * .0001f;
    return true;
}
