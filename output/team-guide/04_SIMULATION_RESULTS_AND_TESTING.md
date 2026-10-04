# WattSense — simulation results and real testing

**Evidence guide · 2 October 2026.** Numbers below come from saved project results and the 30 September audit. We did not collect hardware measurements or rerun the suite while writing this guide.

## 1. Three different kinds of simulation

| Tool | What it helps check | What it cannot establish |
| --- | --- | --- |
| Live dashboard simulator | Explain normal operation, shedding, restore refusal and faults | Actual battery capacity, sensor accuracy or circuit performance |
| Reduced ngspice circuits | Selected electrical behaviour, including I²C rise time and assumed startup transients | Complete operation of the real ESP32, converter, BMS or fan |
| Python battery/converter/load model | Compare policies and explore assumed losses, capacity and supply behaviour | Physical performance until parameters and outputs are validated |

The accelerated battery/load discharge model runs a Python reference controller; the reduced ngspice circuits do not run firmware. Separate host C++ tests check firmware policy logic on the computer. None is an ESP32 hardware-in-the-loop experiment.

## 2. The main runtime comparison

Saved nominal assumptions: 6 Ah capacity; initial SOC 68%; common endpoint 20% reserve; 2.5 W lamp; 2.5 W fan; 0.8 W controller/sensors; 90% converter efficiency; no charging. Loads use constant delivered power in this discharge model. Battery and wiring parameters are assumed.

| Policy | Lamp service | Fan service |
| --- | ---: | ---: |
| Baseline: keep both loads until the common endpoint | 5.4764 h | 5.4764 h |
| Priority: shed fan under the 3-hour policy | 7.8836 h | 2.4936 h |

The lamp gains about **2.4072 hours, or 43.96%**, while fan service decreases by **54.47%**. The gain comes from stopping the fan earlier. It is not a capacity increase, a conversion-efficiency improvement or an experimental result.

The runtime shown by the controller is an estimate at that moment. The total lamp service above is measured within the simulated experiment until its common endpoint. These are different quantities.

Eighteen paired sensitivity cases vary capacity, assumed efficiency and battery/BMS resistance. They are selected deterministic scenarios, not a confidence interval or a promise that real hardware will fall within their range.

## 3. What the electrical models taught us

### Fan startup can be harder than continuous operation

A fan may require a short higher-current pulse when starting. The reduced circuits assumed a 100 ms startup demand and modelled the source, wiring/path drops and capacitance. Their current demands are specified at 5 V as equivalent resistive loads; actual model current falls with voltage. A real fan can stall or restart differently.

| Assumed scenario | Minimum common 5 V rail | Meaning |
| --- | ---: | --- |
| Starter: 0.5 A lamp/fan running; 1.0 A fan startup; 2 A source | 4.791 V | Passes the provisional screen with limited margin |
| 0.6 A lamp/fan running; 1.8 A fan startup; 1.5 A source | 2.995 V | Fails the screen |
| Same limited-source case, capacitor increased from 470 to 2200 µF | 2.995 V | Still fails; extra capacitance cannot sustain the shortage |
| 0.6 A lamp/fan running; 1.8 A fan startup; 3 A source | 4.694 V | Series voltage drop still causes failure |

The screening floor is **4.75 V at the common rail**. It is not an established fan operating limit or ESP32 reset threshold. Fan-terminal voltage can be lower still. Passing the screen does not prove startup or fuse survival. These source settings do not increase the PCB's continuous current limits.

Use the actual selected converter, fan and wiring in an oscilloscope test. Capture the 5 V rail, fan terminals and ESP32 3.3 V rail; a roughly 1 Hz dashboard cannot resolve a short startup dip. Do not change converter capacitors from this model alone: the actual regulator's stability matters.

### I²C edges need checking too

Under the assumed 400 pF bus capacitance, the RC calculation gave approximately 1,593 ns rise time with 4.7 kΩ pull-ups and 746 ns with 2.2 kΩ. Rev B therefore uses 2.2 kΩ for SDA/SCL. These are predicted edges, not measurements; the assembled cable and devices still need checking.

## 4. What the recorded audit proves

The 30 September record reports:

- **45 Python tests** and **67 host C++ assertions** passing; both firmware targets compile.
- **12,000 C++/Python comparison steps** agree on policy behaviour for the tested sequences.
- Numerical checks and saved simulation CSV reproducibility pass.
- Configured CAD electrical/design-rule and connectivity checks pass. An all-rules run reports six connector footprint-filter metadata warnings, described in the hardware guide.

Passing a suite means the expected results occurred, including deliberately failing startup scenarios. It does not mean every candidate load arrangement is acceptable. CAD rules do not certify thermal performance, noise immunity or safe physical assembly.

## 5. The real measurement plan

1. **Assembly and initial power:** follow the staged hardware guide, current-limited supply and full assembly procedure before attaching a battery.
2. **Calibration:** compare voltage and current against an independent instrument, then test held-out readings that were not used to calculate the correction. Targets are voltage ±1% and current ±(3% of reference + 10 mA), not achieved claims. At 1 A the current target is ±40 mA. Include reference-instrument uncertainty.
3. **Battery reference:** verify actual capacity and the legitimate full-charge procedure. Do not treat a template calibration file as measured data.
4. **Switching and faults:** check startup/reset OFF, low-runtime shedding, refused/accepted restore, invalid readings and interrupted integration.
5. **Startup and temperature:** capture transient rail behaviour; record temperatures under the maximum intended load. A DS18B20 at one location does not measure every PCB hotspot.
6. **Matched runtime trials:** compare `MIN_H 0` baseline with `MIN_H 3` priority after valid reference/restore procedures. Baseline disables early runtime shedding, not other protections. Use the same starting charge, loads, controller supply, ambient conditions and independently tracked endpoint. Stop manually at that endpoint; disconnect charging for the first comparison. Repeat and report both lamp and fan service.

Keep raw CSVs, calibration records, instrument details, scope traces, component identities and firmware/configuration versions. Name each record **simulated** or **measured** correctly. If hardware disagrees with a model, update the assumptions and report the difference.

Full-project sources: `docs/HARDWARE_PERFORMANCE.md`, `docs/TEST_PLAN.md`, `docs/RECHECK_2026-09-30.md`, `simulations/hardware-assumptions.json` and `simulations/results/hardware-summary.json`.
