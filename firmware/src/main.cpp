#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <Preferences.h>
#include "config.h"
#include "controller.h"
#include "ina219_checked.h"

Adafruit_INA219 batterySensor(BATTERY_SENSOR_ADDRESS);
Adafruit_INA219 loadSensor(LOAD_SENSOR_ADDRESS);
Adafruit_INA219 solarSensor(SOLAR_SENSOR_ADDRESS);
OneWire oneWire(PIN_TEMPERATURE);
DallasTemperature temperature(&oneWire);
Preferences preferences;
Controller controller;
Sample currentSample;
bool batteryReady = false, loadReady = false, solarReady = false;
float temperatureC = NAN;
uint32_t lastSampleMs = 0, lastPublishMs = 0, lastTemperatureMs = 0, lastSaveMs = 0;
String input;
bool commandOverflow = false;
float savedCheckpoint = NAN;

bool readRegister(uint8_t address, uint8_t reg, uint16_t& value) {
    Wire.beginTransmission(address);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) return false;
    if (Wire.requestFrom(address, (uint8_t)2) != 2) return false;
    value = (uint16_t)Wire.read() << 8;
    value |= Wire.read();
    return true;
}

bool readMonitor(uint8_t address, Ina219Reading& reading) {
    return readIna219Checked([address](uint8_t reg, uint16_t& value) {
        return readRegister(address, reg, value);
    }, reading);
}

bool initSensor(Adafruit_INA219& sensor) {
    if (!sensor.begin(&Wire)) return false;
    sensor.setCalibration_32V_2A();
    return true;
}

Sample measure() {
    Sample sample;
    Ina219Reading battery, load, solar;
    if (!batteryReady) batteryReady = initSensor(batterySensor);
    if (!loadReady) loadReady = initSensor(loadSensor);
    if (SOLAR_SENSOR_FITTED && !solarReady) solarReady = initSensor(solarSensor);
    if (!batteryReady || !loadReady ||
        !readMonitor(BATTERY_SENSOR_ADDRESS, battery) || !readMonitor(LOAD_SENSOR_ADDRESS, load)) {
        batteryReady = loadReady = false;
        return sample;
    }
    // Battery IN+ is protected battery positive, IN- is system junction.
    // INA219 bus voltage is at IN-: add the signed shunt drop for IN+ voltage.
    sample.batteryV = (battery.busV + battery.shuntV) * BATTERY_VOLTAGE_GAIN;
    sample.batteryA = battery.currentA *
                     BATTERY_CURRENT_GAIN - BATTERY_CURRENT_OFFSET_A;
    const float loadA = load.currentA *
                       LOAD_CURRENT_GAIN - LOAD_CURRENT_OFFSET_A;
    const float loadInputV = load.busV + load.shuntV;
    // A small calibrated zero-current residual must not prevent a no-load
    // reference. A significant reverse current in this branch is still invalid.
    sample.loadW = loadInputV * fmaxf(0.0f, loadA);
    sample.temperatureC = temperatureC;
    if (SOLAR_SENSOR_FITTED) {
        if (!solarReady || !readMonitor(SOLAR_SENSOR_ADDRESS, solar)) {
            solarReady = false;
            return sample;
        }
        const float solarA = solar.currentA *
                            SOLAR_CURRENT_GAIN - SOLAR_CURRENT_OFFSET_A;
        sample.solarW = solar.busV * solarA;
        if (!isfinite(solarA) || fabsf(solarA) > MAX_PATH_CURRENT_A) return sample;
    }
    // Unfitted solar sensor remains null, never a claimed zero measurement.
    sample.valid = isfinite(sample.batteryV) && isfinite(sample.batteryA) &&
                   isfinite(sample.loadW) && isfinite(sample.temperatureC) &&
                   sample.batteryV >= 8 && sample.batteryV <= 16 &&
                   fabsf(sample.batteryA) <= MAX_PATH_CURRENT_A &&
                   loadA >= -0.02f && fabsf(loadA) <= MAX_PATH_CURRENT_A && sample.loadW >= 0 &&
                   sample.loadW <= 35 && sample.temperatureC >= -10 &&
                   sample.temperatureC <= 70;
    return sample;
}

void jsonNumber(JsonDocument& doc, const char* key, float number) {
    if (isfinite(number)) doc[key] = number;
    else doc[key] = nullptr;
}

void publish(uint32_t now) {
    StaticJsonDocument<1536> doc;
    doc["protocol"] = 1;
    doc["source_mode"] = "hardware";
    doc["device_id"] = "WATTSENSE-ESP32";
    doc["uptime_ms"] = now;
    doc["sensor_ok"] = currentSample.valid;
    jsonNumber(doc, "battery_v", currentSample.batteryV);
    jsonNumber(doc, "battery_a", currentSample.batteryA);
    jsonNumber(doc, "battery_w", currentSample.batteryV * currentSample.batteryA);
    jsonNumber(doc, "load_w", currentSample.loadW);
    jsonNumber(doc, "solar_w", currentSample.solarW);
    jsonNumber(doc, "temperature_c", currentSample.temperatureC);
    jsonNumber(doc, "soc_pct", controller.socPct);
    jsonNumber(doc, "usable_energy_wh", controller.energyWh);
    jsonNumber(doc, "runtime_h", controller.runtimeH);
    jsonNumber(doc, "runtime_no_solar_h", controller.noSolarRuntimeH);
    doc["estimate_valid"] = isfinite(controller.socPct);
    doc["optional_on"] = controller.optionalOn && HARDWARE_CONFIRMED;
    doc["hardware_armed"] = HARDWARE_CONFIRMED;
    doc["state"] = controller.state;
    doc["reason"] = controller.reason;
    doc["minimum_runtime_h"] = controller.minimumRuntimeH;
    doc["reserve_pct"] = RESERVE_PCT;
    doc["capacity_ah"] = CAPACITY_AH;
    serializeJson(doc, Serial);
    Serial.println();
}

void reply(const char* message) {
    StaticJsonDocument<384> doc;
    doc["type"] = "ack";
    doc["message"] = message;
    serializeJson(doc, Serial);
    Serial.println();
}

bool confirmFullReference() {
    // An explicit operator action is required. These plausibility checks alone
    // are not a full-charge detector.
    if (currentSample.valid && currentSample.batteryV >= 13.4f &&
        currentSample.batteryV <= HIGH_OPERATING_V && fabsf(currentSample.batteryA) <= 0.10f) {
        controller.syncFull();
        reply("Manual full-charge reference accepted. Accuracy still requires calibration.");
        return true;
    }
    reply("Reference refused. Check charged/rested pack and near-zero measured battery current.");
    return false;
}

void handleCommand(String command) {
    command.trim();
    if (command == "OFF") {
        controller.manualOff();
        digitalWrite(PIN_OPTIONAL_ENABLE, LOW);
        reply("Optional output off.");
    } else if (command == "RESTORE") {
        reply(controller.restore(currentSample) ? "Restore accepted." :
              "Restore refused: check hardware lock, charge reference, measurements and runtime margin.");
    } else if (command == "SYNC_FULL_CONFIRMED") {
        confirmFullReference();
    } else if (command.startsWith("MIN_H ")) {
        const String argument = command.substring(6);
        char* end = nullptr;
        const float value = strtof(argument.c_str(), &end);
        if (end != argument.c_str() && *end == '\0' && isfinite(value) && value >= 0 && value <= 12) {
            controller.minimumRuntimeH = value;
            reply("Backup requirement updated.");
        } else reply("Invalid value. Use MIN_H followed by 0 to 12.");
    } else reply("Commands: OFF, RESTORE, MIN_H <0..12>, SYNC_FULL_CONFIRMED");
}

void setup() {
    // External gate/driver pulldown is still required during reset and boot.
    digitalWrite(PIN_OPTIONAL_ENABLE, LOW);
    pinMode(PIN_OPTIONAL_ENABLE, OUTPUT);
    pinMode(PIN_LOAD_BUTTON, INPUT_PULLUP);
    pinMode(PIN_SYNC_BUTTON, INPUT_PULLUP);
    Serial.begin(115200);
    Wire.begin(PIN_SDA, PIN_SCL);
    Wire.setClock(100000);
    Wire.setTimeOut(20);
    batteryReady = initSensor(batterySensor);
    loadReady = initSensor(loadSensor);
    if (SOLAR_SENSOR_FITTED) solarReady = initSensor(solarSensor);
    temperature.begin();
    temperature.setResolution(10);
    temperature.setWaitForConversion(false);
    temperature.requestTemperatures();
    lastTemperatureMs = millis();
    preferences.begin("wattsense", false);
    savedCheckpoint = preferences.getFloat("soc_checkpoint", NAN);
    // Checkpoint is diagnostic only: power-off battery usage is unknown.
    // Do not silently re-use it as an accurate boot-time charge reference.
    input.reserve(100);
    lastSampleMs = millis();
    reply("Booted with optional output OFF and charge estimate unknown.");
}

void loop() {
    const uint32_t now = millis();
    if ((uint32_t)(now - lastTemperatureMs) >= 1000) {
        const float reading = temperature.getTempCByIndex(0);
        temperatureC = reading == DEVICE_DISCONNECTED_C || reading == 85.0f ? NAN : reading;
        temperature.requestTemperatures();
        lastTemperatureMs = now;
    }
    if ((uint32_t)(now - lastSampleMs) >= 100) {
        const float dt = (uint32_t)(now - lastSampleMs) / 1000.0f;
        lastSampleMs = now;
        currentSample = measure();
        controller.update(currentSample, dt);
        digitalWrite(PIN_OPTIONAL_ENABLE, controller.optionalOn && HARDWARE_CONFIRMED ? HIGH : LOW);
    }
    static bool previousButton = HIGH;
    static uint32_t lastButtonMs = 0;
    const bool button = digitalRead(PIN_LOAD_BUTTON);
    if (!button && previousButton && (uint32_t)(now - lastButtonMs) > 300) {
        if (controller.optionalOn) controller.manualOff();
        else controller.restore(currentSample);
        lastButtonMs = now;
    }
    previousButton = button;
    static bool syncHeld = false, syncHandled = false;
    static uint32_t syncStartMs = 0;
    if (digitalRead(PIN_SYNC_BUTTON) == LOW) {
        if (!syncHeld) {
            syncHeld = true;
            syncHandled = false;
            syncStartMs = now;
        }
        if (!syncHandled && (uint32_t)(now - syncStartMs) >= 5000) {
            confirmFullReference();
            syncHandled = true;
        }
    } else {
        syncHeld = false;
        syncHandled = false;
    }
    while (Serial.available()) {
        const char ch = Serial.read();
        if (ch == '\n') {
            if (!commandOverflow) handleCommand(input);
            else reply("Command too long; discarded.");
            input = "";
            commandOverflow = false;
        } else if (ch != '\r' && !commandOverflow) {
            if (input.length() < 96) input += ch;
            else commandOverflow = true;
        }
    }
    if ((uint32_t)(now - lastPublishMs) >= 1000) {
        publish(now);
        lastPublishMs = now;
    }
    if ((uint32_t)(now - lastSaveMs) >= 60000 && isfinite(controller.socPct)) {
        if (!isfinite(savedCheckpoint) || fabsf(controller.socPct - savedCheckpoint) >= .1f) {
            preferences.putFloat("soc_checkpoint", controller.socPct);
            savedCheckpoint = controller.socPct;
        }
        lastSaveMs = now;
    }
    delay(1);
}
