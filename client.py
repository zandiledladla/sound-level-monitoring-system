#!/usr/bin/env python3
import socket
from datetime import datetime

UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', UDP_PORT))  # Listen on all interfaces

print(f"""\n
SOUND MONITOR CLIENT
--------------------
Listening on port {UDP_PORT}
(Ctrl+C to quit)
""")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if "ALERT" in msg:
            print(f"\033[91m{timestamp} - {msg}\033[0m")  # Red for alerts
        else:
            print(f"{timestamp} - {msg}", end='\r')

except KeyboardInterrupt:
    print("\nClient stopped")
finally:
    sock.close()