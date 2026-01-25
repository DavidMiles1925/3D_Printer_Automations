#!/usr/bin/env python3

import subprocess
import time
from datetime import timedelta
import os

UPS_NAME = "apcups"      # same name you used in your bash script
UPSCMD = "/usr/bin/upsc"
REFRESH_SECONDS = 5


def get_ups_data():
    """
    Runs `upsc <upsname>` and parses the key:value output into a dict.
    """
    try:
        result = subprocess.run(
            [UPSCMD, UPS_NAME],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error talking to UPS:", e)
        return {}

    data = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data


def seconds_to_minutes(seconds_str):
    try:
        seconds = int(float(seconds_str))
        return int(seconds / 60)
    except (ValueError, TypeError):
        return None


def print_status(data):
    status = data.get("ups.status", "unknown")
    charge = data.get("battery.charge")
    runtime_sec = data.get("battery.runtime")
    load = data.get("ups.load")
    vin = data.get("input.voltage")
    battvolt = data.get("battery.voltage")

    runtime_min = seconds_to_minutes(runtime_sec)

    os.system("clear")
    print("=" * 50)
    print(f"UPS Status      : {status}")
    if charge:
        print(f"Battery Charge : {charge}%")
    if runtime_min is not None:
        print(f"Runtime Left   : ~{runtime_min} minutes")
    if load:
        print(f"Load           : {load}%")
    if vin:
        print(f"Input Voltage  : {vin} V")
    if battvolt:
        print(f"Output Voltage : {battvolt} V")


def main():
    try:
        while True:
            data = get_ups_data()
            if data:
                print_status(data)
            else:
                print("No data received from UPS")

            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        print("Program was closed using CTRL-C")



if __name__ == "__main__":
    main()
