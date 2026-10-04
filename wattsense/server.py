"""Local HTTP dashboard, simulator, serial reader and timestamped CSV recorder."""
import argparse
from collections import deque
import csv
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
from pathlib import Path
import threading
import time
from urllib.parse import urlparse
from .simulator import Simulator

ROOT = Path(__file__).resolve().parent.parent
FIELDS = [
    "received_at", "source_mode", "device_id", "uptime_ms", "sensor_ok",
    "battery_v", "battery_a", "battery_w", "load_w", "solar_w", "temperature_c",
    "soc_pct", "estimate_valid", "usable_energy_wh", "runtime_h", "runtime_no_solar_h",
    "optional_on", "state", "reason", "minimum_runtime_h", "reserve_pct",
    "capacity_ah", "hardware_armed",
]
NUMERIC = ("battery_v", "battery_a", "battery_w", "load_w", "solar_w", "temperature_c",
           "soc_pct", "usable_energy_wh", "runtime_h", "runtime_no_solar_h")
STATES = {"NORMAL", "RECOVERY", "WATCH", "PRIORITY", "RESERVE", "MANUAL_OFF",
          "SENSOR_FAULT", "UNCALIBRATED", "TEMPERATURE", "HARDWARE_LOCKED"}


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def parse_telemetry(line):
    """Only accept the documented hardware protocol; never substitute simulated data."""
    if len(line) > 8192:
        raise ValueError("Telemetry line too long.")
    try:
        data = json.loads(line)
    except (ValueError, RecursionError) as exc:
        raise ValueError("Invalid telemetry JSON.") from exc
    if not isinstance(data, dict) or type(data.get("protocol")) is not int or data["protocol"] != 1:
        raise ValueError("Unsupported telemetry protocol.")
    if data.get("source_mode") != "hardware":
        raise ValueError("Serial telemetry must identify itself as hardware.")
    if any(key not in data for key in FIELDS if key != "received_at"):
        raise ValueError("Incomplete telemetry frame.")
    if not isinstance(data.get("state"), str) or data["state"] not in STATES:
        raise ValueError("Unknown controller state.")
    for key in NUMERIC:
        value = data.get(key)
        if value is not None and not finite_number(value):
            raise ValueError("Invalid numeric field: " + key)
    for key in ("sensor_ok", "estimate_valid", "optional_on", "hardware_armed"):
        if not isinstance(data.get(key), bool):
            raise ValueError("Invalid boolean field: " + key)
    for key in ("minimum_runtime_h", "reserve_pct", "capacity_ah", "uptime_ms"):
        value = data.get(key)
        if not finite_number(value):
            raise ValueError("Invalid configuration field: " + key)
    if not 0 <= data["reserve_pct"] < 100 or not 0 < data["capacity_ah"] <= 100:
        raise ValueError("Invalid battery configuration.")
    if not 0 <= data["minimum_runtime_h"] <= 24 or type(data["uptime_ms"]) is not int or not 0 <= data["uptime_ms"] <= 0xFFFFFFFF:
        raise ValueError("Invalid runtime or uptime.")
    if data["soc_pct"] is not None and not 0 <= data["soc_pct"] <= 100:
        raise ValueError("Invalid charge estimate.")
    if data["estimate_valid"] != (data["soc_pct"] is not None):
        raise ValueError("Charge estimate and validity flag disagree.")
    if data["estimate_valid"] and not data["sensor_ok"]:
        raise ValueError("Faulted sensors cannot supply a valid charge estimate.")
    if data["sensor_ok"] and any(data[x] is None for x in ("battery_v", "battery_a", "battery_w", "load_w", "temperature_c")):
        raise ValueError("Healthy frame has missing measurements.")
    if data["sensor_ok"]:
        if not (8 <= data["battery_v"] <= 16 and abs(data["battery_a"]) <= 2 and
                0 <= data["load_w"] <= 35 and -10 <= data["temperature_c"] <= 70 and
                (data["solar_w"] is None or abs(data["solar_w"]) <= 35)):
            raise ValueError("Healthy measurements exceed the prototype range.")
        if abs(data["battery_w"] - data["battery_v"] * data["battery_a"]) > .05:
            raise ValueError("Battery power disagrees with signed voltage/current.")
    if data["optional_on"] and not (data["hardware_armed"] and data["sensor_ok"] and data["estimate_valid"]):
        raise ValueError("Output-on frame contradicts lock or measurement state.")
    if any(data[key] is not None and data[key] < 0 for key in ("usable_energy_wh", "runtime_h", "runtime_no_solar_h")):
        raise ValueError("Negative energy/runtime estimate.")
    if not isinstance(data["device_id"], str) or not 1 <= len(data["device_id"]) <= 64:
        raise ValueError("Invalid device identity.")
    if not isinstance(data["reason"], str) or len(data["reason"]) > 300:
        raise ValueError("Invalid reason.")
    return {key: data[key] for key in FIELDS if key != "received_at"}


class Session:
    def __init__(self, mode="simulated", log_dir=None):
        self.mode = mode
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.simulator = Simulator() if mode == "simulated" else None
        self.latest = None
        self.last_seen = None
        self.history = deque(maxlen=600)
        self.events = deque(maxlen=50)
        self.error = None
        self.samples = 0
        self.last_state = None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        log_dir = Path(log_dir or ROOT / "logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = log_dir / f"{mode}-{stamp}.csv"
        self.log_file = self.log_path.open("w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.log_file, FIELDS, extrasaction="ignore")
        self.writer.writeheader()
        self.log_file.flush()
        self.add_event("Session started", "Illustrative simulator; no physical measurements." if self.simulator
                       else "Waiting for real USB serial telemetry. Dashboard is read-only.")

    def add_event(self, title, detail):
        self.events.appendleft({"at": datetime.now(timezone.utc).isoformat(),
                                "title": title, "detail": detail})

    def record(self, data):
        with self.lock:
            row = dict(data, received_at=datetime.now(timezone.utc).isoformat())
            self.last_seen = time.monotonic()
            self.latest = row
            self.history.append(row)
            # Preserve numbers as numbers; prevent text fields from becoming
            # spreadsheet formulas when a CSV is opened in Excel/LibreOffice.
            csv_row = {key: ("'" + value if isinstance(value, str) and
                            value.startswith(("=", "+", "-", "@", "\t", "\r")) else value)
                       for key, value in row.items()}
            self.writer.writerow(csv_row)
            self.log_file.flush()
            self.samples += 1
            self.error = None
            if data["state"] != self.last_state:
                self.add_event(data["state"].replace("_", " ").title(), data["reason"])
                self.last_state = data["state"]

    def snapshot(self):
        with self.lock:
            age = None if self.last_seen is None else max(0, time.monotonic() - self.last_seen)
            return {"mode": self.mode, "latest": self.latest, "history": list(self.history),
                    "events": list(self.events), "stale": age is None or age > 3,
                    "age_s": age, "samples": self.samples, "error": self.error,
                    "log_name": self.log_path.name, "controls_enabled": self.mode == "simulated",
                    "scenario_name": self.simulator.scenario_name if self.simulator else None}

    def command(self, data):
        with self.lock:
            if self.simulator is None:
                raise PermissionError("Hardware dashboard is read-only. Use the documented local firmware controls.")
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            message = self.simulator.command(data)
            if data.get("action") == "scenario":
                self.history.clear()
                self.last_state = None
            self.add_event("Simulator control", message)
            return message

    def export(self):
        with self.lock:
            self.log_file.flush()
            return self.log_path.read_bytes()

    def close(self):
        self.stop.set()
        with self.lock:
            self.log_file.close()


def simulation_worker(session):
    next_log = time.monotonic()
    last_step = time.monotonic()
    while not session.stop.wait(0.1):
        now = time.monotonic()
        with session.lock:
            frame = session.simulator.step(now - last_step)
            last_step = now
            if now >= next_log:
                session.record(frame)
                next_log = now + 1


def serial_worker(session, port, baud):
    import serial
    while not session.stop.is_set():
        try:
            with serial.Serial(port, baudrate=baud, timeout=1) as stream:
                with session.lock:
                    session.add_event("Serial connected", port + "; waiting for protocol version 1.")
                while not session.stop.is_set():
                    line = stream.read_until(b"\n", 8193)
                    if not line:
                        continue
                    if not line.endswith(b"\n"):
                        # Discard any incomplete/oversized frame; never parse its tail as telemetry.
                        stream.reset_input_buffer()
                        continue
                    try:
                        frame = parse_telemetry(line.decode("utf-8"))
                    except (ValueError, UnicodeError):
                        continue  # ROM boot messages and command acknowledgements are not samples.
                    session.record(frame)
        except (serial.SerialException, OSError) as exc:
            with session.lock:
                session.error = "Serial connection unavailable: " + str(exc)
            session.stop.wait(2)


def handler_for(session):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, body, code=200, kind="application/json; charset=utf-8", filename=None):
            if not isinstance(body, bytes):
                body = json.dumps(body, allow_nan=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'self'")
            if filename:
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def local_request(self):
            allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            return host in allowed and (origin is None or origin in {"http://" + h for h in allowed})

        def do_GET(self):
            if not self.local_request():
                self.respond({"error": "Local dashboard requests only."}, 403)
                return
            path = urlparse(self.path).path
            if path == "/api/state":
                self.respond(session.snapshot())
            elif path == "/api/export":
                self.respond(session.export(), kind="text/csv; charset=utf-8", filename=session.log_path.name)
            elif path in ("/", "/app.js", "/style.css"):
                filename = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}[path]
                mime = {"/": "text/html", "/app.js": "application/javascript", "/style.css": "text/css"}[path]
                self.respond((ROOT / "web" / filename).read_bytes(), kind=mime + "; charset=utf-8")
            elif path == "/favicon.ico":
                self.respond(b"", 204, "image/x-icon")
            else:
                self.respond({"error": "Not found."}, 404)

        def do_POST(self):
            if not self.local_request():
                self.respond({"error": "Local dashboard requests only."}, 403)
                return
            if self.path != "/api/control":
                self.respond({"error": "Not found."}, 404)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 4096 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    raise ValueError("Send a JSON object smaller than 4 KB.")
                body = json.loads(self.rfile.read(size))
                self.respond({"message": session.command(body)})
            except PermissionError as exc:
                self.respond({"error": str(exc)}, 403)
            except (ValueError, TypeError, RecursionError, OverflowError) as exc:
                self.respond({"error": str(exc)}, 400)
    return Handler


def main():
    parser = argparse.ArgumentParser(description="Wattsense local dashboard")
    parser.add_argument("--mode", choices=("simulated", "hardware"), default="simulated")
    parser.add_argument("--serial-port", help="Required for hardware mode, for example COM5")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--list-ports", action="store_true")
    args = parser.parse_args()
    if args.list_ports:
        try:
            from serial.tools.list_ports import comports
            for port in comports():
                print(port.device, "-", port.description)
        except ImportError:
            parser.error("Install requirements.txt to list serial ports.")
        return
    if args.mode == "hardware":
        if not args.serial_port:
            parser.error("--serial-port is required in hardware mode; simulation will not be substituted.")
        try:
            import serial
        except ImportError:
            parser.error("Hardware mode needs pyserial. Install requirements.txt.")
    session = Session(args.mode)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(session))
    except OSError:
        session.close()
        raise
    worker = threading.Thread(target=simulation_worker if args.mode == "simulated" else serial_worker,
                              args=(session,) if args.mode == "simulated" else (session, args.serial_port, args.baud),
                              daemon=True)
    worker.start()
    print(f"Wattsense: http://127.0.0.1:{args.port} | {args.mode.upper()}", flush=True)
    print(f"Log: {session.log_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        session.stop.set()
        server.server_close()
        worker.join(timeout=4)
        session.close()


if __name__ == "__main__":
    main()
