import csv
import io
import json
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from wattsense.server import Session, handler_for, parse_telemetry, serial_worker
from wattsense.simulator import Simulator


def hardware_frame():
    data = Simulator().step()
    data["source_mode"] = "hardware"
    data["device_id"] = "TEST-FIXTURE"
    data["hardware_armed"] = True
    return data


class ProtocolTests(unittest.TestCase):
    def test_serial_reader_survives_bad_frame_then_records_valid_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            session=Session('hardware',directory)
            lines=[json.dumps(dict(hardware_frame(),state=[])).encode()+b'\n',
                   json.dumps(hardware_frame()).encode()+b'\n']
            class FakeSerial:
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def read_until(self,*args):
                    if lines:return lines.pop(0)
                    session.stop.set();return b''
            try:
                with patch('serial.Serial',return_value=FakeSerial()):
                    serial_worker(session,'FAKE-TEST-PORT',115200)
                self.assertEqual(session.samples,1)
                self.assertEqual(session.latest['device_id'],'TEST-FIXTURE')
            finally:session.close()

    def test_frame_preserves_negative_charging_and_missing_solar(self):
        data = hardware_frame()
        data["battery_a"] = -.5
        data["battery_w"] = -.5 * data["battery_v"]
        data["solar_w"] = None
        result = parse_telemetry(json.dumps(data))
        self.assertEqual(result["battery_a"], -.5)
        self.assertIsNone(result["solar_w"])

    def test_reject_fake_hardware_and_bad_frames(self):
        for data in [Simulator().step(), {}, [], dict(hardware_frame(), battery_a=float("nan")),
                     dict(hardware_frame(), optional_on="yes"),
                     dict(hardware_frame(), sensor_ok=True, battery_v=None),
                     dict(hardware_frame(), sensor_ok=False, estimate_valid=True),
                     dict(hardware_frame(), soc_pct=101)]:
            with self.assertRaises(ValueError):
                parse_telemetry(json.dumps(data))

    def test_malformed_json_shapes_reject_without_crashing_reader(self):
        for key, value in [('state', []), ('state', {}), ('protocol', True),
                           ('protocol', 1.0), ('uptime_ms', .5)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                parse_telemetry(json.dumps(dict(hardware_frame(), **{key: value})))

    def test_bad_scenario_type_returns_validation_error(self):
        for value in ([], {}, None, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Simulator().reset(value)

    def test_extreme_or_inconsistent_frames_are_rejected(self):
        for changed in ({'battery_a': 10**400}, {'battery_v': 1000},
                        {'battery_w': -999}, {'estimate_valid': False},
                        {'hardware_armed': False}, {'runtime_h': -1},
                        {'uptime_ms': 2**32}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                parse_telemetry(json.dumps(dict(hardware_frame(), **changed)))
        with self.assertRaises(ValueError):
            parse_telemetry('[' * 1200 + '0' + ']' * 1200)

    def test_stale_and_export_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            session = Session("hardware", directory)
            try:
                self.assertTrue(session.snapshot()["stale"])
                session.record(hardware_frame())
                self.assertFalse(session.snapshot()["stale"])
                session.last_seen = time.monotonic() - 4
                self.assertTrue(session.snapshot()["stale"])
                rows = list(csv.DictReader(io.StringIO(session.export().decode())))
                self.assertEqual(rows[0]["source_mode"], "hardware")
                self.assertEqual(rows[0]["device_id"], "TEST-FIXTURE")
                self.assertTrue(rows[0]["received_at"])
            finally:
                session.close()

    def test_csv_text_is_not_a_formula_but_negative_current_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            session = Session("hardware", directory)
            try:
                frame = hardware_frame()
                frame["reason"] = "=1+1"
                frame["battery_a"] = -.5
                session.record(frame)
                row = next(csv.DictReader(io.StringIO(session.export().decode())))
                self.assertEqual(row["reason"], "'=1+1")
                self.assertEqual(float(row["battery_a"]), -.5)
            finally:
                session.close()


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.session = Session("simulated", self.directory.name)
        self.session.record(self.session.simulator.step())
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(self.session))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.session.close()
        self.directory.cleanup()

    def post(self, body, headers=None):
        return urlopen(Request(self.base + "/api/control", json.dumps(body).encode(),
                               {"Content-Type": "application/json", **(headers or {})}), timeout=3)

    def test_simulated_commands_and_logged_data(self):
        with self.post({"action": "scenario", "value": "reserve"}) as response:
            self.assertEqual(response.status, 200)
        for _ in range(40):
            row = self.session.simulator.step(.1)
        self.session.record(row)
        with urlopen(self.base + "/api/state") as response:
            data = json.load(response)
        self.assertFalse(data["latest"]["optional_on"])
        self.assertTrue(data["controls_enabled"])
        with urlopen(self.base + "/api/export") as response:
            self.assertIn(b"simulated", response.read())
            self.assertIn("attachment", response.headers["Content-Disposition"])

    def test_hardware_is_read_only(self):
        self.session.simulator = None
        self.session.mode = "hardware"
        with self.assertRaises(HTTPError) as error:
            self.post({"action": "restore"})
        self.assertEqual(error.exception.code, 403)

    def test_reject_cross_origin_control(self):
        with self.assertRaises(HTTPError) as error:
            self.post({"action": "optional_off"}, {"Origin": "https://example.com"})
        self.assertEqual(error.exception.code, 403)

    def test_bad_input_and_unknown_paths(self):
        with self.assertRaises(HTTPError) as error:
            self.post({"action": "minimum_runtime", "value": -1})
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base + "/../README.md")
        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
