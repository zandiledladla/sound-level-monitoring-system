#!/usr/bin/env python3
"""Read a GPIO sound sensor and send debounced UDP events."""
from __future__ import annotations

import argparse
import logging
import socket
import time
from collections.abc import Iterator
from contextlib import closing

from monitor import SoundEventMonitor

LOGGER = logging.getLogger("sound_monitor")


def simulated_readings() -> Iterator[bool]:
    """Produce repeatable readings for demos without Raspberry Pi hardware."""
    cycle = 0
    while True:
        yield cycle % 40 in {10, 11, 25}
        cycle += 1


def run(readings: Iterator[bool], destination: tuple[str, int], *,
        debounce: float, status_interval: float, poll_interval: float) -> None:
    monitor = SoundEventMonitor(debounce, status_interval)
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp_socket:
        for detected in readings:
            message = monitor.process(detected, time.time())
            if message:
                udp_socket.sendto(message.to_bytes(), destination)
                LOGGER.info("sent %s to %s:%s", message.type, *destination)
            time.sleep(poll_interval)


def gpio_readings(pin: int) -> Iterator[bool]:
    """Yield digital readings and always release GPIO resources."""
    try:
        import RPi.GPIO as GPIO
    except ImportError as error:
        raise RuntimeError("RPi.GPIO is required unless --simulate is used") from error
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    try:
        while True:
            yield GPIO.input(pin) == GPIO.HIGH
    finally:
        GPIO.cleanup()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--pin", type=int, default=17)
    parser.add_argument("--debounce", type=float, default=0.3)
    parser.add_argument("--status-interval", type=float, default=5.0)
    parser.add_argument("--poll-interval", type=float, default=0.05)
    parser.add_argument("--simulate", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 1 <= args.port <= 65535 or args.poll_interval <= 0:
        raise SystemExit("port must be 1–65535 and poll interval must be positive")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    readings = simulated_readings() if args.simulate else gpio_readings(args.pin)
    LOGGER.info("monitoring GPIO%s; sending to %s:%s", args.pin, args.client_host, args.port)
    try:
        run(readings, (args.client_host, args.port), debounce=args.debounce,
            status_interval=args.status_interval, poll_interval=args.poll_interval)
    except (KeyboardInterrupt, RuntimeError) as error:
        LOGGER.info("monitor stopped: %s", error or "requested by user")


if __name__ == "__main__":
    main()
