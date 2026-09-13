import json
import unittest

from client import parse_message
from monitor import MonitorMessage, SoundEventMonitor


class SoundEventMonitorTests(unittest.TestCase):
    def test_alert_is_debounced(self):
        monitor = SoundEventMonitor(debounce_seconds=1.0, status_seconds=5.0)
        self.assertEqual(monitor.process(True, 10.0).type, "sound_alert")
        self.assertIsNone(monitor.process(True, 10.5))
        self.assertEqual(monitor.process(True, 11.0).type, "sound_alert")

    def test_status_uses_independent_interval(self):
        monitor = SoundEventMonitor(status_seconds=5.0)
        self.assertIsNone(monitor.process(False, 4.9))
        self.assertEqual(monitor.process(False, 5.0).type, "status")
        self.assertIsNone(monitor.process(False, 9.9))

    def test_message_serialises_as_json(self):
        payload = MonitorMessage("sound_alert", True, "2026-01-01T00:00:00+00:00").to_bytes()
        self.assertEqual(json.loads(payload)["detected"], True)
        self.assertEqual(parse_message(payload)["type"], "sound_alert")

    def test_invalid_message_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_message(b"not-json")
        with self.assertRaises(ValueError):
            parse_message(b'{"type":"status"}')

    def test_invalid_intervals_are_rejected(self):
        with self.assertRaises(ValueError):
            SoundEventMonitor(debounce_seconds=-1)


if __name__ == "__main__":
    unittest.main()
