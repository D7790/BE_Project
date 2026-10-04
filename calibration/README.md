# Calibration records

`measurements-template.csv` has blank measurement cells. Copy it for your lab session and fill only independently observed measurements. Instructions, node mapping, meter use, accepted ranges and CLI commands are in `../docs/LAB_START_GUIDE.md`.

`examples/simulated-measurements.csv` and the generated `examples/simulated-report.json` demonstrate the calculation using deliberately synthetic numbers. They are not measurements and their correction constants must not be applied to hardware. Synthetic data requires the explicit `--allow-simulated` CLI flag.

Keep each actual session's original readings, date, instruments/ranges, wiring arrangement and notes. Generated reports retain an input SHA-256 hash; this links the calculation to a file but does not authenticate its contents. Review corrections, apply approved constants manually, rebuild and verify with additional physical measurements.
