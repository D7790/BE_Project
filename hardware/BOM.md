# Purchase specification

**Current purchasing entry point:** [Pune buying plan, 28 September 2026](BUYING_PLAN_PUNE.md) has supplier leads, unresolved compatibility checks and the four-layer budget allocation. [Supplier questions](SUPPLIER_QUESTIONS.md) are ready for the team to send. The table below is retained only as the earlier module-based alternative; do not use it as the revision B shopping list.

These are allowances from the project blueprint, not confirmed quotations or orders. No parts have been purchased.

**Custom PCB alternative:** the current four-layer revision B has its own `pcb/wattsense-main-revB-4layer/BOM.csv` and grouped purchasing list. Revision A remains separately available as a two-layer alternative. Use the BOM matching the chosen revision; B changes R4/R5 to 2.2 kOhm. These boards replace the INA219 modules and separate switching driver below. Do not buy both sets. The Rs 9,500 total below is the earlier module-based allowance; obtain fresh delivered quotations before claiming either custom-board version fits below Rs 10,000.

| Item | Qty | Required checks | Allowance |
| --- | ---: | --- | ---: |
| Protected 4S LiFePO4 pack, about 6 Ah | 1 | Documented charge voltage/current, protected terminals, BMS functions and temperature limits | ₹2,200 |
| Matching enclosed charger | 1 | Correct chemistry, voltage, current and polarity | ₹650 |
| Classic ESP32 development board + data cable | 1 | GPIO21/22/25/27/4 accessible; exact board pinout | ₹450 |
| INA219 modules | 3 | 0.1-ohm shunt reference, ratings, 3.3 V I2C and configurable addresses | ₹750 |
| DS18B20 + pull-up, two buttons and passives | Set | Powered three-wire sensor; actual pinout | ₹150 |
| 5 V DC converter | 1 | Full pack-voltage input range, verified load/startup current | ₹250 |
| DC switching driver(s) | 1–2 | Active-high 3.3 V control, startup-off behavior, current and suppression | ₹300 |
| Small 5 V lamp and fan | Set | Start around 2.5 W / 0.5 A class each; measure <=0.6 A per branch and qualify startup; total 5 V continuous load <=7.5 W / 1.5 A including ESP32 | ₹450 |
| Fuse, disconnect, terminals, wiring and enclosure | Set | Correct DC/current ratings, secure connections | ₹650 |
| **Battery prototype** | | | **₹5,850** |
| Nominal 20 W solar panel | 1 | Worst-case open-circuit voltage and current compatible with charger | ₹1,750 |
| 4S LiFePO4 solar controller | 1 | Actual charge settings and input limits; not a generic lead-acid-only unit | ₹1,100 |
| Shipping/replacements | | | ₹800 |
| **Target including solar** | | | **₹9,500** |

Buy the first two INA219s for the review and add the third with solar. Borrow lab equipment. A fabricated carrier PCB needs a separate delivered quote and may require replacing some perfboard spending or borrowing the solar panel to remain under ₹10,000.

Record supplier, exact model, delivered price and arrival date before buying. See the original blueprint for the dated price references; stock may have changed.
