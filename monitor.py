"""Hardware-independent sound-event monitoring logic."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MonitorMessage:
    type: str
    detected: bool
    timestamp: str

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")


class SoundEventMonitor:
    """Turn digital sensor readings into debounced alerts and status updates."""

    def __init__(self, debounce_seconds: float = 0.3, status_seconds: float = 5.0):
        if debounce_seconds < 0 or status_seconds <= 0:
            raise ValueError("debounce must be non-negative and status interval positive")
        self.debounce_seconds = debounce_seconds
        self.status_seconds = status_seconds
        self.last_alert_at: float | None = None
        self.last_status_at: float = 0.0

    def process(self, detected: bool, now: float) -> MonitorMessage | None:
        if detected and (
            self.last_alert_at is None or now - self.last_alert_at >= self.debounce_seconds
        ):
            self.last_alert_at = now
            return self._message("sound_alert", True, now)
        if not detected and now - self.last_status_at >= self.status_seconds:
            self.last_status_at = now
            return self._message("status", False, now)
        return None

    @staticmethod
    def _message(message_type: str, detected: bool, now: float) -> MonitorMessage:
        timestamp = datetime.fromtimestamp(now, timezone.utc).isoformat()
        return MonitorMessage(message_type, detected, timestamp)
