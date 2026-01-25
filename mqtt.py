#!/usr/bin/env python3
import json
import subprocess
import paho.mqtt.client as mqtt
import time
from config import X1_CARBON_SERIAL

# --- CONFIGURATION ---
PRINTER_IP = "192.168.1.159"       # Replace with your printer's static IP
ACCESS_CODE = "<LAN_ACCESS_CODE>"  # Access code from LAN-only / developer mode
UPS_TOPIC = "/tmp/ups_event.txt"   # Optional: file or message broker for UPS events
NTFY_TOPIC = "pikachupoweroutage1925"

# MQTT topics
REPORT_TOPIC = "device/+/report"
REQUEST_TOPIC_TEMPLATE = "device/{serial}/request"

# --- FUNCTIONS ---
def send_ntfy(message: str, priority: str = "high"):
    """Send a notification via ntfy."""
    subprocess.run([
        "/usr/local/bin/ntfy",
        "publish", NTFY_TOPIC,
        "--priority", priority,
        message
    ])

def pause_print(client, serial):
    """Send pause command to printer."""
    topic = REQUEST_TOPIC_TEMPLATE.format(serial=serial)
    payload = {"command": "pause"}
    client.publish(topic, json.dumps(payload))
    send_ntfy(f"⏸️ Print paused on printer {serial} due to power outage", "high")

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected to printer MQTT with result code {rc}")
    client.subscribe(REPORT_TOPIC)

def on_message(client, userdata, msg):
    """Handle incoming messages from the printer."""
    try:
        data = json.loads(msg.payload.decode())
        serial = data.get("device", {}).get("serial", "unknown")
        state = data.get("state", "")
        # You can log or print printer state
        print(f"Printer {serial} state: {state}")
    except Exception as e:
        print("Error parsing MQTT message:", e)

# --- MAIN ---
def main():
    # MQTT client setup
    client = mqtt.Client()
    client.username_pw_set("bblp", ACCESS_CODE)
    client.tls_set()  # MQTTs over TLS
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(PRINTER_IP, 8883, 60)
    client.loop_start()

    send_ntfy("✅ Bambu MQTT monitor started", "normal")

    try:
        while True:
            # Check UPS events
            # For demo, reading from a text file written by your UPS script
            try:
                with open(UPS_TOPIC) as f:
                    event = f.read().strip()
                    if event == "ONBATT":
                        # Pause all printers — loop over serials if needed
                        pause_print(client, X1_CARBON_SERIAL)  # Replace with real serial
                        # Clear the event so we don’t repeat
                        open(UPS_TOPIC, "w").close()
            except FileNotFoundError:
                pass

            time.sleep(5)

    except KeyboardInterrupt:
        print("Exiting...")
        client.loop_stop()

if __name__ == "__main__":
    main()
