// Dedicated read-only diagnostic build. No command can turn on GPIO25.
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include "config.h"
#include "ina219_checked.h"

Adafruit_INA219 monitors[] = {Adafruit_INA219(BATTERY_SENSOR_ADDRESS), Adafruit_INA219(LOAD_SENSOR_ADDRESS), Adafruit_INA219(SOLAR_SENSOR_ADDRESS)};
const uint8_t addresses[] = {BATTERY_SENSOR_ADDRESS,LOAD_SENSOR_ADDRESS,SOLAR_SENSOR_ADDRESS};
const char* channels[] = {"battery","load","charger"};
bool ready[] = {false,false,false};
OneWire oneWire(PIN_TEMPERATURE);
DallasTemperature temperature(&oneWire);
uint32_t lastReport=0;

bool readRegisterAt(uint8_t address,uint8_t reg,uint16_t& value) {
    Wire.beginTransmission(address); Wire.write(reg);
    if (Wire.endTransmission(false)!=0 || Wire.requestFrom(address,uint8_t(2))!=2) return false;
    value=uint16_t(Wire.read())<<8; value|=Wire.read(); return true;
}

void scan() {
    StaticJsonDocument<1024> doc;
    doc["type"]="bringup_scan"; doc["source_mode"]="hardware_diagnostic";
    doc["optional_output_commanded_on"]=false;
    JsonArray found=doc.createNestedArray("addresses_decimal");
    for (uint8_t address=8;address<120;address++) {
        Wire.beginTransmission(address);
        if (Wire.endTransmission()==0) found.add(address);
    }
    serializeJson(doc,Serial); Serial.println();
}

void setup() {
    digitalWrite(PIN_OPTIONAL_ENABLE,LOW); pinMode(PIN_OPTIONAL_ENABLE,OUTPUT);
    pinMode(PIN_LOAD_BUTTON,INPUT_PULLUP); pinMode(PIN_SYNC_BUTTON,INPUT_PULLUP);
    Serial.begin(115200); Wire.begin(PIN_SDA,PIN_SCL); Wire.setClock(100000); Wire.setTimeOut(20);
    temperature.begin(); temperature.setResolution(10); temperature.setWaitForConversion(false);
    temperature.requestTemperatures();
    scan();
    for (unsigned i=0;i<3;i++) {
        ready[i]=monitors[i].begin(&Wire);
        if (ready[i]) monitors[i].setCalibration_32V_2A();
    }
    lastReport=millis();
}

void loop() {
    digitalWrite(PIN_OPTIONAL_ENABLE,LOW);
    // Input is consumed and ignored. There is no restore/sync/enable interface.
    while (Serial.available()) Serial.read();
    if (uint32_t(millis()-lastReport)<1000) { delay(1); return; }
    lastReport=millis();
    StaticJsonDocument<2048> doc;
    doc["type"]="bringup"; doc["source_mode"]="hardware_diagnostic";
    doc["uptime_ms"]=lastReport; doc["optional_output_commanded_on"]=false;
    doc["load_button_pressed"]=digitalRead(PIN_LOAD_BUTTON)==LOW;
    doc["full_button_pressed"]=digitalRead(PIN_SYNC_BUTTON)==LOW;
    const float temp=temperature.getTempCByIndex(0);
    if (isfinite(temp) && temp!=DEVICE_DISCONNECTED_C && temp!=85 && temp>=-10 && temp<=70) doc["temperature_c"]=temp;
    else doc["temperature_c"]=nullptr;
    temperature.requestTemperatures();
    JsonArray sensors=doc.createNestedArray("sensors");
    for (unsigned i=0;i<3;i++) {
        if (!ready[i]) {
            ready[i]=monitors[i].begin(&Wire);
            if (ready[i]) monitors[i].setCalibration_32V_2A();
        }
        Ina219Reading r;
        const bool ok=ready[i] && readIna219Checked([i](uint8_t reg,uint16_t& v) {
            return readRegisterAt(addresses[i],reg,v);
        },r);
        if (!ok) ready[i]=false;
        JsonObject item=sensors.createNestedObject();
        item["channel"]=channels[i]; item["address_decimal"]=addresses[i]; item["valid"]=ok;
        if (ok) {
            item["raw_bus_v"]=r.busV; item["raw_input_v"]=r.busV+r.shuntV;
            item["raw_shunt_mv"]=r.shuntV*1000; item["raw_current_a"]=r.currentA;
        } else {
            item["raw_bus_v"]=nullptr; item["raw_input_v"]=nullptr;
            item["raw_shunt_mv"]=nullptr; item["raw_current_a"]=nullptr;
        }
    }
    serializeJson(doc,Serial); Serial.println();
}
