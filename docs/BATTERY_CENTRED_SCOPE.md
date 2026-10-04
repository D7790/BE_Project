# WattSense battery monitor and energy signature adviser

**Current scope clarified on 3 October 2026.** WattSense mounts near the battery and runs from it through a qualified regulator. It estimates remaining charge, usable energy and backup time, then uses known load profiles and user priorities to recommend which optional loads to turn off. Review 3: 3 October 2026; final submission: next semester.

## Power and information flow

```text
Solar panel -> compatible solar controller ------+
                                                |
Mains -> compatible AC-to-DC battery charger -----+-> protected DC bus
                                                |
Battery with commercial BMS <-> rated signed-current sensor

DC bus -> converters -> DC loads
DC bus -> inverter -> AC loads
DC bus -> regulated supply -> WattSense monitor

Battery V/I/temperature + supporting load readings
    -> charge/usable-energy estimate + known load profiles
    -> runtime estimate -> optional-load recommendation
```

Select one approved charging path initially. The BMS protects the pack; the charger/controller manages charging; the inverter supplies AC loads. WattSense monitors and advises. The solar controller regulates panel power before it reaches the battery bus. A lead-acid UPS charger must not charge a LiFePO4 pack without explicit manufacturer compatibility.

Whole-battery sensing must cover **all charging and discharge paths**, including the monitor's own consumption. The existing Rev B PCB remains a low-power DC foundation with provisional **2 A battery-path** and **1.5 A continuous 5 V** ceilings. It cannot carry household-inverter current or connect to mains. A larger backup setup needs separately rated sensing/power hardware or documented compatible UPS telemetry. Supporting AC measurements require a rated enclosed meter and documented isolated data interface; a custom mains PCB or BMS is not mandatory.

## Estimation and signature development

Charge estimation needs a valid starting reference and independently established usable capacity. Runtime depends on reserve, demand and conversion losses. Battery-side demand already includes inverter losses; avoid adding them twice. Treat future solar availability as uncertain.

Start with 4–6 known AC/DC load profiles and controlled individual recordings on the actual converter/inverter arrangement. Aggregate battery current alone cannot uniquely identify every appliance, particularly during charging. Supporting load measurements can improve attribution. Compare a Random Forest candidate with Decision Tree and feature matching in local Python; hold out complete sessions. UNKNOWN/ambiguous handling must be validated. Later deployment inside the battery-powered device requires resource and interface qualification.

Measured Wh, inferred per-load consumption and predicted backup are different outputs. Recommendations are advisory: the user switches off the chosen load. No automatic mains control, recognition accuracy or energy savings has been demonstrated.

## Current evidence and next steps

Existing software, dashboard, simulations and unbuilt DC CAD are the foundation. Physical assembly, calibration, measured signatures and the combined adviser remain pending. First qualify battery-powered monitoring and data acquisition, collect profiles, evaluate estimates/advice, then test compatible AC/DC backup arrangements.

The budget remains **below ₹10,000**, with expanded delivered cost unconfirmed. The old ₹9,700 DC allocation excludes added inverter/AC equipment; borrow suitable lab equipment where possible. Historical paper, workbook and teammate guides need scope alignment before reuse. Code, CAD and hardware-arming flags remain unchanged.
