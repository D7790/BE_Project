#pragma once
#include <math.h>
#include "config.h"

struct Sample {
    float batteryV = NAN;
    float batteryA = NAN;
    float loadW = NAN;
    float solarW = NAN;
    float temperatureC = NAN;
    bool valid = false;
};

// Validate at the policy boundary as well as in the I2C acquisition layer.
inline bool usableSample(const Sample& s) {
    return s.valid && isfinite(s.batteryV) && isfinite(s.batteryA) &&
        isfinite(s.loadW) && isfinite(s.temperatureC) &&
        s.batteryV >= 8 && s.batteryV <= 16 &&
        fabsf(s.batteryA) <= MAX_PATH_CURRENT_A && s.loadW >= 0 && s.loadW <= 35 &&
        s.temperatureC >= -10 && s.temperatureC <= 70 &&
        (!SOLAR_SENSOR_FITTED || (isfinite(s.solarW) && fabsf(s.solarW) <= 35));
}

class Controller {
public:
    // At 10 Hz, small increments can round away in a float SOC accumulator.
    double socPct = NAN;
    float energyWh = NAN;
    float runtimeH = NAN;
    float noSolarRuntimeH = NAN;
    float minimumRuntimeH = MINIMUM_RUNTIME_H;
    bool optionalOn = false;
    const char* state = "UNCALIBRATED";
    const char* reason = "Manual charge reference required after every reboot.";

    void syncFull() {
        socPct = 100.0f;
        filteredW = NAN;
        belowForS = 0;
    }

    void manualOff() {
        optionalOn = false;
        requested = false;
        policyShed = false;
        belowForS = 0;
    }

    bool restore(const Sample& sample) {
        if (!HARDWARE_CONFIRMED || !usableSample(sample) || !isfinite(socPct) ||
            !isfinite(minimumRuntimeH) || minimumRuntimeH < 0 || minimumRuntimeH > 24 ||
            socPct <= RESERVE_PCT || sample.temperatureC >= MAX_SURFACE_TEMPERATURE_C ||
            sample.batteryV <= LOW_OPERATING_V || sample.batteryV > HIGH_OPERATING_V)
            return false;
        const float prospectiveW = sample.loadW + (optionalOn ? 0 : OPTIONAL_INPUT_POWER_W);
        if (prospectiveW <= 0.2f || !isfinite(prospectiveW)) return false;
        const float availableWh = (socPct - RESERVE_PCT) * 0.01f * CAPACITY_AH * NOMINAL_V;
        if (availableWh / prospectiveW < minimumRuntimeH + RESTORE_MARGIN_H) return false;
        optionalOn = true;
        policyShed = false;
        requested = true;
        belowForS = 0;
        return true;
    }

    void update(const Sample& sample, float dt) {
        if (!usableSample(sample) || !isfinite(dt) || dt <= 0 || dt > 2.0f ||
            !isfinite(minimumRuntimeH) || minimumRuntimeH < 0 || minimumRuntimeH > 24) {
            socPct = energyWh = runtimeH = noSolarRuntimeH = filteredW = NAN;
            optionalOn = false;
            policyShed = false;
            belowForS = 0;
            state = "SENSOR_FAULT";
            reason = "Invalid sensor data or integration gap; charge reference invalidated.";
            return;
        }
        if (!isfinite(socPct)) {
            optionalOn = false;
            state = HARDWARE_CONFIRMED ? "UNCALIBRATED" : "HARDWARE_LOCKED";
            reason = "Output off. Verify hardware and establish a manual full-charge reference.";
            return;
        }
        const float effectiveA = sample.batteryA *
            (sample.batteryA < 0 ? CHARGE_EFFICIENCY : 1.0f);
        socPct = fmin(100.0, fmax(0.0, socPct - 100.0 * effectiveA * dt / (3600.0 * CAPACITY_AH)));
        const float rawW = sample.batteryV * sample.batteryA;
        filteredW = isfinite(filteredW) ? filteredW + (1 - expf(-dt / 3)) * (rawW - filteredW) : rawW;
        energyWh = fmaxf(0, socPct - RESERVE_PCT) * 0.01f * CAPACITY_AH * NOMINAL_V;
        runtimeH = filteredW > 0.2f ? energyWh / filteredW : NAN;
        noSolarRuntimeH = sample.loadW > 0.2f ? energyWh / sample.loadW : NAN;
        if (!HARDWARE_CONFIRMED) {
            optionalOn = false;
            state = "HARDWARE_LOCKED";
            reason = "Physical output disabled in config.h pending hardware review.";
        } else if (sample.temperatureC >= MAX_SURFACE_TEMPERATURE_C) {
            optionalOn = false;
            belowForS = 0;
            state = "TEMPERATURE";
            reason = "Surface temperature at or above configured limit; optional load off.";
        } else if (sample.batteryV > HIGH_OPERATING_V ||
                   sample.batteryV <= LOW_OPERATING_V || socPct <= RESERVE_PCT) {
            optionalOn = false;
            belowForS = 0;
            state = "RESERVE";
            reason = "Configured voltage or charge operating limit reached.";
        } else if (!requested) {
            optionalOn = false;
            state = "MANUAL_OFF";
            reason = "Optional load disabled by the local operator.";
        } else if (isfinite(noSolarRuntimeH) && noSolarRuntimeH < minimumRuntimeH) {
            belowForS += dt;
            // Thirty 0.1f samples can sum just below 3.0f; allow only float rounding.
            if (belowForS + 0.00001f >= SHED_DELAY_S) {
                optionalOn = false;
                policyShed = true;
                state = "PRIORITY";
                reason = "Backup-time requirement exceeded; optional load shed.";
            } else {
                state = "WATCH";
                reason = "Checking sustained backup-time condition.";
            }
        } else {
            belowForS = 0;
            state = optionalOn ? "NORMAL" : policyShed ? "PRIORITY" : "RECOVERY";
            reason = optionalOn ? "Loads within the configured operating policy." :
                policyShed ? "Backup policy shed the optional load; local restoration requires sufficient margin." :
                "Optional load remains off until a local restore request.";
        }
    }
private:
    float filteredW = NAN;
    float belowForS = 0;
    bool requested = true;
    bool policyShed = false;
};
