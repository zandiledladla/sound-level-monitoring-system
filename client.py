#!/usr/bin/env python3
"""Receive and display structured sound-monitor events over UDP."""
from __future__ import annotations

import argparse
import json
import socket
from contextlib import closing


def parse_message(payload: bytes) -> dict:
    try:
        message = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("received an invalid JSON message") from error
    required = {"type", "detected", "timestamp"}
    if not required.issubset(message):
        raise ValueError("message is missing required fields")
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5005)
    args = parser.parse_args()
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp_socket:
        udp_socket.bind((args.host, args.port))
        print(f"Listening for sound events on {args.host}:{args.port} (Ctrl+C to stop)")
        try:
            while True:
                payload, sender = udp_socket.recvfrom(4096)
                try:
                    message = parse_message(payload)
                    label = "ALERT" if message["detected"] else "STATUS"
                    print(f'{label} {message["timestamp"]} from {sender[0]}')
                except ValueError as error:
                    print(f"Ignored message from {sender[0]}: {error}")
        except KeyboardInterrupt:
            print("\nClient stopped")


if __name__ == "__main__":
    main()
