#!/usr/bin/env python3
import RPi.GPIO as GPIO
import socket
import time
import subprocess

# ===== Hardware Config =====
SOUND_SENSOR_PIN = 17  # Verify your working pin
UDP_PORT = 5005
CLIENT_IP = '172.21.12.41'  # Your client IP
DEBOUNCE_TIME = 0.3  # 300ms debounce period

# ===== GPIO Setup =====
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# ===== Network Setup =====
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_ip = subprocess.getoutput("hostname -I").split()[0]

print(f"""
SOUND MONITORING SERVER (DEBOUNCED)
---
Sensor: GPIO{SOUND_SENSOR_PIN}
Server IP: {server_ip}
Port: {UDP_PORT}
Debounce: {DEBOUNCE_TIME}s
""")

last_alert_time = 0  # Track last alert time

try:
    while True:
        current_state = GPIO.input(SOUND_SENSOR_PIN)
        current_time = time.time()
        
        # Only send alert if: HIGH state AND enough time passed since last alert
        if current_state == GPIO.HIGH and (current_time - last_alert_time) > DEBOUNCE_TIME:
            alert_msg = f"ALERT: Sound detected at {time.ctime()}"
            sock.sendto(alert_msg.encode(), (CLIENT_IP, UDP_PORT))
            print(alert_msg)
            last_alert_time = current_time  # Update last alert time
            
            # Add visual feedback (optional)
            print("Sensor State: HIGH")
        else:
            # Only send normal status occasionally to reduce network traffic
            if current_time - last_alert_time > 5:  # Every 5 seconds
                sock.sendto(b"STATUS: Normal", (CLIENT_IP, UDP_PORT))
                print("Sensor State: LOW")
        
        time.sleep(0.05)  # Shorter sleep for responsiveness

except KeyboardInterrupt:
    print("Server stopped by user.")
finally:
    GPIO.cleanup()
    sock.close()