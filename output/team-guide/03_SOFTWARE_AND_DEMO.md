# WattSense: software, demonstration and firmware

**Team guide — 2 October 2026.** Read this before demonstrating the dashboard or changing code. Hardware is not assembled or validated. This document describes existing files and recorded checks; preparing it did not rerun tests.

## 1. What runs where?

| Part | Responsibility | Main project files |
| --- | --- | --- |
| ESP32 firmware | Read real sensors, estimate charge, decide whether the fan may run, send readings | `firmware/src/main.cpp`, `firmware/include/controller.h`, `firmware/include/config.h` |
| Python collector/server | Receive USB serial readings, serve the local dashboard, save CSV records | `wattsense/server.py` |
| Browser dashboard | Display measurements, plots, state and event history | `web/` |
| Live teaching simulator | Generate illustrative readings and exercise the Python reference policy without hardware | `wattsense/simulator.py`, `wattsense/model.py` |
| Offline simulation suite | Test software, run accelerated battery/load models and reduced electrical circuits, produce figures | `simulations/` |

In hardware mode, **the ESP32 makes control decisions**. The dashboard is read-only. A laptop provides display/logging; if USB is the ESP32's only supply, disconnecting it also removes controller power.

The live dashboard simulator is not the detailed electrical simulation. Neither is proof that an assembled circuit works. Host C++ tests execute controller logic on the computer, not on an ESP32.

## 2. Understand the control rule

1. On reset, the fan command is OFF and **SOC (estimated charge percentage) is unknown**. The firmware does not guess percentage from voltage.
2. After a verified charge-reference procedure, measured current is accumulated over time. Positive battery current means discharge; negative means charging.
3. The controller estimates available energy above the provisional 20% reserve. Its priority decision assumes **no future charging**; some upstream losses are omitted, so runtime is a heuristic, not a guaranteed minimum.
4. When estimated runtime stays below **3 hours for 3 seconds**, the optional fan switches off. The essential lamp remains powered.
5. The fan stays off until an explicit restore request passes all checks. At the default setting, runtime **including the fan's expected extra consumption** must be at least **3.25 hours**. That extra-power assumption needs measurement.
6. Invalid readings or an integration gap longer than **2 seconds** invalidate SOC and disable the fan. Temperature/voltage limits also restrict operation.

Current production settings are `HARDWARE_CONFIRMED=false` and `SOLAR_SENSOR_FITTED=false`. Keep them unchanged until the documented lab qualification is completed. A simulated solar scenario does not mean physical solar hardware exists. A mains charger connected through U3 is not solar generation.

## 3. Run the software demonstration on Windows

**You need the project code separately. This Markdown guide bundle is not a runnable project.** Open PowerShell in the project root—the folder containing `README.md` and `run_demo.ps1`.

Install Python 3.10 or newer first if necessary. On a new computer, create its own environment; do not copy another machine's `.venv`:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m wattsense.server --mode simulated
```

The live simulator/dashboard use Python's standard library: no pip package, cloud account or API key is required. Python installation may need internet; the prepared demo works locally. If the environment already exists, run just the last command, or `.\run_demo.ps1`.

Open **http://127.0.0.1:8765** in a browser. Keep the PowerShell window running. Confirm the dashboard says **SIMULATED**.

### Two-minute walkthrough

1. **Normal load:** explain charge, battery current, power and estimated runtime. These are illustrative readings.
2. **Limited backup:** wait about four seconds; show the fan changing to OFF while essential lighting is retained in the model.
3. **Restore fan:** demonstrate refusal when prospective runtime is insufficient. A button request cannot force the policy to accept it.
4. **Solar charging:** show negative battery current. Explain that future sunshine is not promised in the priority estimate.
5. **Sensor disconnected:** show unknown charge/runtime and fan OFF.
6. **Export session CSV:** save the recording with its simulated source label.

Scenario selection resets the illustrative reference and visible chart. The session CSV retains earlier records, including reset discontinuities. This live model uses real elapsed time; it is not the accelerated hours-long experiment.

Press **Ctrl+C** in the server terminal to stop. `stop_demo.ps1` only stops a separately recorded background demo after checking its process identity. If port 8765 is busy, check the existing server before starting another.

## 4. Reproduce tests and build firmware later

The live demo uses only the standard library, but the software tests also need `pyserial`. Install the project requirements first (the initial installation may need internet):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Firmware builds need downloaded packages on first use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_firmware.ps1
.\build_firmware.ps1 -Environment bringup
```

These commands **compile only; they do not upload**. The script creates a checked `.ws-pio` junction under the user profile to a project-local cache; it refuses an unrelated existing path. The `bringup` target holds the fan OFF and reports raw diagnostics, which are separate from dashboard telemetry.

For the full simulation suite, install KiCad 10 with its Python/ngspice components, then:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-simulation.txt
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE '.ws-pio'
.\.venv\Scripts\python.exe -m platformio pkg install --global --tool platformio/toolchain-gccmingw32@1.50100.0
.\run_simulations.ps1
```

Run the build setup above first. For a nondefault KiCad installation, follow the `NGSPICE_DLL` and `KICAD_PYTHON` overrides in `simulations/README.md`. Results/logs are written to `simulations/results/`; preserve previous evidence before rerunning.

The **30 September recorded audit** reports 45 Python tests, 67 host C++ assertions and both firmware builds passing. This is software evidence, not hardware certification.

## 5. Connect real serial telemetry only after lab preparation

Use the qualified board/procedure in `docs/LAB_START_GUIDE.md`, `firmware/README.md` and `hardware/REFERENCE_WIRING.md` first. For production telemetry:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m wattsense.server --list-ports
.\run_hardware.ps1 -SerialPort COM5
```

Replace `COM5` with the detected port. Hardware mode never silently substitutes simulated data. Only one application can own the serial port; close the collector before using a terminal. Reopening serial may reset the ESP32 and invalidate its reference. Follow the verified full-charge procedure; pressing a reference button does not charge the battery.
