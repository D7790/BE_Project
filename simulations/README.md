# Reproducible simulation suite

Run `run_simulations.ps1` from the project root. It executes Python tests, host C++ policy tests, ngspice reduced circuits, accelerated ideal and nonideal plant runs, startup scenarios and plot generation. It stops on a failed command and saves logs in `results/`.

Requirements already installed on this machine:

- Project `.venv`, Python 3.12; `requirements-simulation.txt` provides matplotlib for figures.
- KiCad 10, including `C:/Program Files/KiCad/10.0/bin/ngspice.dll` (ngspice 46). Override the DLL path with `NGSPICE_DLL` if necessary. The adapter is Windows-specific.
- Project-local PlatformIO tool package `platformio/toolchain-gccmingw32@1.50100.0`. Host binaries and temporary configuration copies live in `.local/host-policy-tests/`. To install elsewhere, use the same project-local `PLATFORMIO_CORE_DIR` as `build_firmware.ps1` and run `python -m platformio pkg install --global --tool platformio/toolchain-gccmingw32@1.50100.0`.

The production `firmware/include/config.h` remains `HARDWARE_CONFIRMED=false`. The host suite tests a locked copy and a separately armed temporary copy; neither flashes nor controls hardware. Host tests run the actual C++ controller header but do not emulate ESP32 peripherals or instruction timing.

Current suite: 45 Python tests and 67 native C++ assertions (16 locked policy, 27 armed-copy policy, 24 register-reader). Eight Python tests check the new electrical equations, invalid points and power conservation. The policy tests include small-current accumulation at 10 Hz. The checked INA219 reader is exercised using fake register transactions, including failures, sensor resets and lost calibration. This is not an electrical bus simulation. Calibration tests use synthetic fixtures; the runnable CSV example is in `../calibration/examples/`. The suite hashes production `.cpp` files, headers, tests, web assets, assumptions and PlatformIO configuration as well as the Python sources.

`run_spice.py` checks the CAD audit hashes and matching component values/topology before executing nine reduced circuits. `.cir` files are saved for inspection or reuse with standalone ngspice. They use ideal sources, built-in resistors/capacitors/inductors, a behavioural switch and a generic diode. The current monitors, converter, BMS, charger, actual fan electronics, PCB parasitics, temperature and EMC are not simulated. KiCad's bundled DLL reports a missing `spinit` warning; these circuits use only built-in primitive models and ran without simulation errors. The full output is recorded.

`run_system.py` integrates an ideal battery at one-second steps. It compares essential-load service to a 20% true reserve, includes nine capacity/efficiency pairs, seven fault injections and a capacity/offset error example. This is an explicitly idealized plant, not a LiFePO4 electrochemical model. Baseline and controlled runs share assumptions. The fan is sacrificed to extend lamp service; battery capacity is not increased.

Read `../docs/SIMULATION_REPORT.md` for results and limitations. Figures are saved as both PNG and SVG, with underlying CSV data. Never relabel them as experimental measurements in the review.

`run_hardware.py` adds a lumped battery/constant-power/load-loss model, 18 paired sensitivity cases, time-step convergence checks, and six behavioural current-limited startup circuits. It invokes `extract_copper.py` with KiCad's Python to read explicit path geometry; set `KICAD_PYTHON` to override `C:/Program Files/KiCad/10.0/bin/python.exe`. It verifies the previous power-path audit's PCB hash and does not modify native CAD. Ground planes, thermal effects, exact converter/motor dynamics and protective trips are not modeled. Some startup cases intentionally fail their voltage screen: the suite must correctly expose those failures.

`hardware-assumptions.json` separates invented/assumed pack, wiring, load and module values from manufacturer nominal component resistances. Replacing these assumptions with independent measurements is the next development step. This accelerated model does not replace the live dashboard's simple teaching simulator. Read `../docs/HARDWARE_PERFORMANCE.md` for interpretation and `../docs/PROJECT_FLOW.md` for operation and next lab steps.
