# Wattsense buying plan — Pune 411048

Checked 28 September 2026. Four students; nothing purchased; total hardware budget **below INR 10,000**. Public web listings below are leads, not carts, paid orders or delivered quotes. Stock, tax, shipping, minimum-order charges and delivery to 411048 must be confirmed at ordering. No supplier has been contacted and no files have been uploaded for a quote.

## Recommended purchase sequence

1. Start with the ESP32, USB data cable, DS18B20, buttons and wire. Use the college supply and meter. Buy the buck converter only after checking its exact variant and qualify its output/current limiting in the lab.
2. Get a delivered **four-layer** bare-board quote and the full revision B parts total together. Order one populated prototype's parts, plus a few low-cost assembly spares. Do not buy three complete INA219 modules and a separate MOSFET module for this custom-PCB build.
3. Buy a protected 12.8 V 4S LiFePO4 pack and its supplier-confirmed matched charger as a compatible pair after the PCB/bench bring-up. A separate custom BMS is unnecessary. Keep solar hardware optional/borrowed until the core battery experiment works and the budget permits it.

**Load selection update from simulation:** start with roughly 2.5 W / 0.5 A class 5 V lamp and fan, then verify actual current stays below 0.6 A per branch and 1.5 A total continuously including the ESP32. Check the fan's permitted voltage range and startup current/duration. A 3 W constant-power load can exceed 0.6 A after voltage drop; a module's printed current rating does not prove startup performance. See `docs/HARDWARE_PERFORMANCE.md`. Prices and quotes below were not refreshed by this simulation work.

## Public component leads

Prices are observed unit listings in INR; do not assume GST or freight inclusion. Vendor stock labels are not a promise of dispatch or delivery. The full 50-location PCB BOM is in `pcb/wattsense-main-revB-4layer/BOM-grouped.csv`.

| Item | Qty | Observed unit listing | Source | Selection status |
| --- | ---: | ---: | --- | --- |
| Classic ESP32 development board, Type-C CH340C | 1 | 349 | [iFuture product](https://ifuturetech.org/product/esp32-development-board-type-c-ch340c-wifibluetooth/) | Starter candidate; confirm ESP32/WROOM-32 type, 3.3 V signals, exposed GPIO4/21/22/25/26/27 and documented 5 V input. C3/S3 are not automatic substitutes. |
| Powered DS18B20 probe | 1 | 60 | [iFuture product](https://ifuturetech.org/product/ds18b20-waterproof-digital-temperature-sensor/) | Starter candidate; verify lead functions, powered three-wire connection and actual accuracy. |
| LM2596 buck module with display | 1 | 115 | [iFuture product](https://ifuturetech.org/product/lm2596-dc-dc-buck-converter-module-with-voltmeter-display/) | Candidate only; qualify 5 V regulation, current limiting and heat at actual load. A regulator module is not a battery charger. |
| INA219AIDR, SOIC-8, distributor cut tape | 3 | 214.99 | [DigiKey part listing](https://www.digikey.in/en/products/detail/texas-instruments/INA219AIDR/1984881) | Correct purchase code/package for U1–U3. Three at the observed single-unit price = 644.97, before unconfirmed extras. Select cut tape; a custom reel can add fees. |
| Phoenix Contact 1715721 terminals | 6 | 109.02 | [Mouser part listing](https://www.mouser.in/en/ProductDetail/Phoenix-Contact/1715721?qs=BYlwlsDsB%2FqgmKyTCSucHg%3D%3D) | Exact footprint reference; six at this price = 654.12 before extras. Any cheaper substitute needs pitch, drill, body and wire-entry checks before purchase. |
| AshvaVolt 12.8 V 6 Ah LiFePO4 pack with BMS | 1 | 1,534 | [Manufacturer/store listing](https://ashvavolt.com/product/ashvavolt-12-8v-6ah-76-8w-li-fe-lithium-iron-phosphate-solar-inverter-battery-with-bms-protection-and-1-years-warranty/) | **Hold for compatibility confirmation:** common-port protected terminals, connector/polarity and compatible 14.6 V charger. Pack rating does not increase this PCB's 2 A ceiling. |
| Goldstar 14.6 V 1 A charger | 1 | 750 | [Store listing](https://goldstarstore.in/products/14-6v-1a-lithium-battery-charger-wall-mounted) | **Unresolved lead, not a purchase recommendation.** Page has ambiguous chemistry/nominal-voltage wording and availability indications. Confirm 4S LiFePO4, 12.8 V nominal, correct CC/CV termination, polarity and availability with the pack supplier. |

The ESP32/probe/buck listings total **INR 524** before any unconfirmed extras; cable, buttons, leads and shipping are additional. Prefer combining small-item orders or local pickup after checking exact specifications to avoid repeated freight charges.

### Ordering-code correction

[TI lists INA219AIDR as active and INA219AID tube as obsolete](https://www.ti.com/product/INA219/part-details/INA219AIDR). They are carrier variants of the same SOIC-8 product. Revision B's schematic values, PCB values, design manifest and purchasing BOM now use **INA219AIDR**; no layout change was required. `INA219AIDCNR` uses another package/pinout and is not a drop-in part. Revision A is preserved as historical design data and needs the purchasing update if selected later.

Also source all three **WSL2512R1000FEA** shunts, **AO3400A**, **SS14**, **SMBJ15A**, **0466002.NR** main fuse, two **0466001.NR** branch fuses, specified passives, headers and capacitor from the full BOM. The current table does not price every PCB part. R4/R5 are 2.2 kOhm on B; R6 is 4.7 kOhm. Part authenticity, tolerances and package dimensions matter more than a matching listing title.

## Budget limits for deciding whether to order

These are allocation **ceilings**, not supplier quotations. Amounts should include the actual payable batch quantity, tax and delivery assigned to that category; shared shipping must be counted once. Assembly assumes college equipment and team labour. A re-spin is not funded by this plan.

| Category | Maximum allocation (INR) |
| --- | ---: |
| Four-layer bare PCB batch, delivered | 2,500 |
| All parts for one populated PCB, delivered | 2,300 |
| ESP32, temperature probe and qualified buck, delivered | 700 |
| Low-power lamp/fan, cables, two buttons, pack fuse/holder, disconnect, standoffs and insulating base | 700 |
| Protected battery pack, delivered | 1,800 |
| Supplier-matched enclosed 14.6 V charger, initially no more than 1 A, delivered | 1,000 |
| Remaining shipping/assembly spares contingency | 700 |
| **Total planning ceiling** | **9,700** |

Below-INR-10,000 completion is **not yet confirmed**. In particular, the four-layer batch, remaining PCB parts and a verified matched charger remain unquoted. If the delivered total exceeds the ceiling, first borrow a compatible pack/charger or defer solar. Revision A is the available two-layer fallback if needed; update and recheck it before ordering. Extra layers are optional for the electrical scope and do not raise current limits. Keep the requested four-layer B as the preferred candidate while quotes are gathered.

Solar panel/controller purchases are **outside this initial allocation**. The core demonstration is measurement, fault handling, priority control and measured runtime comparison. Describe the solar input as planned/borrowed until a real compatible controller is connected and tested.

## PCB quotes and Pune delivery

Request quotes from [LionCircuits](https://www.lioncircuits.com/) and [PCB Power's quotation page](https://login.pcbpower.com/V2/customer/order/place_order.aspx?access=public), or a college-approved fabricator. Generic introductory prices and website defaults are not quotes for this 100 × 90 mm four-layer design. Ask for total paid batch cost, tooling/stencil/assembly exclusions, GST, shipping and dispatch plus delivery date to **411048**. No PIN-specific delivery date has been verified.

The battery store advertises generic courier timings, but they are not a confirmed 411048 ETA. Do not promise that a PCB or battery will arrive for Review 3. Use the CAD, simulation evidence and lab plan already available; add hardware evidence only when actually measured.

Use `hardware/SUPPLIER_QUESTIONS.md` as the copyable request. It has not been sent. After replies, record the exact part/quote date and payable total here before selecting a build revision.
