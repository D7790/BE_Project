# WattSense — understand the whole project

**Team explanation · 2 October 2026.** This describes the intended physical system and the software/model work already available. Hardware assembly and measurements are pending.

## 1. What problem are we solving?

Imagine a battery supplying a lamp and a fan during an outage. Both use the same limited stored energy. If the fan keeps running, the lamp also stops sooner. Our system gives the lamp higher priority and disconnects the fan when estimated backup becomes limited.

The essential lamp is the demonstration's chosen priority, not a device the system recognises automatically. The fan is explicitly wired to the controllable branch. The first prototype is a small, low-voltage DC system, not a household mains installation.

## 2. What each part does

| Part | Plain explanation |
| --- | --- |
| Protected 4S LiFePO4 battery | Four cells in series store energy; nominal pack voltage is 12.8 V |
| Purchased BMS inside the pack | Protects cells according to the pack's specifications; does not implement our lamp/fan policy |
| Matched charger | Charges that specific pack correctly; the BMS is not a substitute for it |
| Buck converter | Converts battery-level DC into regulated 5 V for the loads |
| Three INA219 sensors on our PCB | Measure small shunt voltage drops and bus voltages to monitor energy flow |
| DS18B20 probe | Measures temperature at its installed location |
| ESP32 development board | Reads measurements, estimates charge/runtime and commands the fan switch |
| MOSFET on our PCB | Acts as the fan's electronic switch |
| Laptop dashboard | Displays and records data received from the ESP32 |

Only one custom PCB is currently needed. It integrates the sensing, fan switch, protection components and connections. The battery, charger, converter and ESP32 remain external modules.

Quick units: **V** is voltage, **A** is current, and **W** is power (`W = V × A`). A 5 V device drawing 0.5 A uses 2.5 W. **Ah** measures accumulated charge; **Wh** measures energy. A nominal 12.8 V, 6 Ah pack has about 76.8 Wh on that nominal basis, before reserve and losses; actual usable energy needs measurement.

## 3. Follow the power and information separately

This is a functional overview, **not a pin-level wiring drawing**. Use the hardware guide and native schematic for wiring.

```text
ENERGY TO THE LOADS
Protected battery -> external fuse/disconnect -> battery sensor U1
    -> system bus -> load sensor U2 -> external 5 V converter
    -> PCB 5 V input and branch fuses -> essential lamp
                                      -> optional fan -> MOSFET return

CHARGING
One compatible charger -> charger sensor U3 -> system bus
    -> battery sensor U1 -> protected battery

INFORMATION AND CONTROL
INA219 measurements + temperature + local buttons
    -> ESP32 estimation and decision -> fan MOSFET
    -> USB serial -> Python collector -> dashboard and CSV
```

Battery charge and discharge must both pass U1. Positive battery current means discharge; negative current means charging. U2 measures the converter's input branch, not separate lamp and fan currents. We cannot claim each appliance's measured power from these three channels alone.

U3 is the charging-input channel. Although some software labels call it solar, a mains charger is not solar generation. A later solar extension needs a compatible charge controller; a raw panel must not connect directly to the battery port.

## 4. How do we estimate battery charge?

**SOC**, or state of charge, is the estimated percentage remaining. Our method is coulomb counting: accumulate measured current over time from a valid known starting point.

For a simple example, a 6 Ah battery supplying 1 A for 30 minutes supplies 0.5 Ah. That is about 8.3 percentage points of its nominal capacity. Actual estimation also depends on sensor calibration, real battery capacity, timing and charging assumptions.

The system starts with **unknown SOC**, not an invented 100%. A real full-charge procedure and reference are needed. Holding the reference button does not physically charge the pack. Resetting the controller or losing measurement continuity can invalidate the estimate.

LiFePO4 voltage is relatively flat over much of its operating range, so our firmware does not simply translate one voltage reading into an accurate percentage.

## 5. How does the fan decision work?

At the default settings:

1. Startup/reset leaves the fan OFF. Measurement validity and a genuine charge reference must be established before normal operation.
2. Estimate usable energy above a provisional 20% reserve and divide by load power to obtain a backup estimate.
3. If estimated runtime stays below **3 hours for 3 seconds**, switch the fan OFF and keep it off.
4. Restore only after an explicit request, valid voltage/temperature/measurements, and an estimate of at least **3.25 hours with the fan included**.
5. Invalid readings or a measurement gap longer than **2 seconds** invalidate the charge reference and disable the optional fan.

The 3.25-hour restore threshold provides margin above the 3-hour shedding threshold. This helps avoid rapid on/off cycling. The fan's additional power is currently a provisional configuration value that must be measured.

The priority-control runtime estimate assumes no future charging and omits some upstream losses. It is a useful decision heuristic, not a guaranteed minimum backup time. The dashboard also has a separate estimate based on net battery flow. The essential lamp is not automatically disconnected by this PCB: a supervised operator must stop the test at its normal endpoint.

## 6. Why is this a final-year engineering project?

The meaningful work is integrating measurement, embedded control, PCB design and experiments. We must show that the current measurements are accurate enough, the fan decision behaves correctly, startup does not collapse the supply, and the hardware remains within its qualified limits.

Our comparison asks: **how much longer does the lamp operate, and how much fan service is lost?** Both results matter. Priority switching is an established idea; our project does not claim a new algorithm.

The existing model predicts longer lamp service, but real performance must be measured. Physical assembly, calibration, fault tests, startup/temperature checks and repeated fair comparisons turn the current design into a completed demonstrator.

Next: [hardware](02_HARDWARE_AND_PCB.md), [software](03_SOFTWARE_AND_DEMO.md) or [test evidence](04_SIMULATION_RESULTS_AND_TESTING.md).
