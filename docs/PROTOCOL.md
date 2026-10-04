# Serial protocol v1

One UTF-8 JSON object per line at 115200 baud. Telemetry includes protocol = 1 and source_mode = "hardware". Boot text and acknowledgement messages are ignored. Simulated samples never enter hardware mode.

| Field | Meaning |
| --- | --- |
| device_id | Device identifier |
| uptime_ms | Device milliseconds since boot, not a UTC timestamp |
| sensor_ok | Boolean indicating validity of required measurements |
| battery_v | Protected pack-side terminal voltage |
| battery_a | Signed battery current; positive discharge, negative charge |
| battery_w | battery_v × battery_a |
| load_w | Power entering the measured load branch |
| solar_w | Controller battery-side contribution; null when not fitted |
| temperature_c | Measured battery surface temperature |
| soc_pct | Estimated charge, or null if unsynchronized |
| estimate_valid | Whether a charge reference remains valid |
| usable_energy_wh | Approximate energy above the configured reserve |
| runtime_h | Estimate using smoothed net battery discharge; null when charging/near idle |
| runtime_no_solar_h | Heuristic runtime estimate assuming no future charge input |
| optional_on | Commanded output state, not independently measured contact state |
| hardware_armed | Build-time physical-control enable status |
| state | Controller state |
| reason | Human-readable reason for that state |
| minimum_runtime_h | Configured backup requirement |
| reserve_pct | Configured charge reserve |
| capacity_ah | Configured capacity |

Non-finite or unknown numbers must be JSON null, never NaN or Infinity. Required booleans must be real JSON booleans.

`runtime_no_solar_h` divides nominal remaining energy above reserve by measured load-branch power. It excludes some upstream losses and cannot predict future load changes or correct unknown capacity error. It is a no-future-charge heuristic, not a guaranteed minimum runtime.

`protocol` is the integer 1; `uptime_ms` is an integer from 0 through 4294967295 (the device counter wraps after about 49.7 days). The collector rejects invalid types, excessive/nested input, implausible healthy readings, negative energy/runtime, inconsistent charge-validity flags and an output-on claim while disarmed or faulted. For healthy frames, battery power must agree with voltage times signed current within 0.05 W to allow serialization rounding. A malformed frame is discarded; subsequent valid frames remain readable. These checks validate format and consistency, not the authenticity of user-supplied serial data.

The collector adds received_at in UTC. Receipt time, a three-second freshness check and source_mode are available in the dashboard/API. Logs are written once per received telemetry frame; the supplied firmware publishes about once per second.

Hardware state values: NORMAL, RECOVERY, WATCH, PRIORITY, RESERVE, MANUAL_OFF, SENSOR_FAULT, UNCALIBRATED, TEMPERATURE and HARDWARE_LOCKED.

Opening a port may reset the device. Repeated uptime or an uptime decrease can indicate a restart; do not join discharge experiments across resets without reviewing continuity.

## Local dashboard interface

- GET /api/state: latest frame, recent history, freshness, session count and events.
- GET /api/export: complete current-session CSV.
- POST /api/control: simulator actions only; hardware sessions return HTTP 403.

Simulator action names: scenario, minimum_runtime, optional_off, restore and fault. Scenario values: normal, reserve, solar and fault.

The server binds to 127.0.0.1 and checks Host/Origin for local requests. This prototype is not configured for public deployment.
