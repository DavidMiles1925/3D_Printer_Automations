# 3D Printer Automations

## Introduction

I live in an area where I experience semi-frequent power outages of varying lengths. At one point I had the power go out with 4 printer running simoultaneously, and that prompted me to look into backup power solutions. Battery backups that could keep my printers running for hours were not financially feasible, so I settled for a system that would allow me to pause and gracefully shut down my printers in the event of power outage, greatly increasing the chances of the print surviving the outage.

However, since the system only gives me as little as 10 minutes to shut down my printers, it is very likely that I will miss the power outage if I am in bed, or just outside of the house. I am developing this suite of automations to help detect and automatically react to power outages. I may expand the capabilities further as use cases present themself.

---

---

## System Development

### Planned Features

- ✔ Load monitoring/response software at Pi startup
  - ✔ Set Up Pi OS
  - ✔ Connect Pi to Power Backup
  - ✔ Write Base Program
- ✔ Detect power/battery status
- ✔ Detect time remaining on battery
- ✔ Upon outage, relay outage status and time remaining message
- Upon outage, send pause command to all printers with built in retries
- Upon printers paused, send shutdown command to plugs
- Upon completion of process, send report message

---

### Hardware in Use

| Hardware                            | Description                                              | Link                                                                             |
| ----------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Tapo Smart Plug (P110M)             | Used to control and monitor printer power.               | [Amazon](https://www.amazon.com/dp/B0DKG52WQ4)                                   |
| APC Back-UPS Pro 1500VA UPS Battery | Provides power to printers during an outage.             | [Amazon](https://www.amazon.com/dp/B06VY6FXMM)                                   |
| Raspberry Pi Zero 2 W               | Used for detection and to control outage reaction logic. | [Micro Center](https://www.microcenter.com/product/643085/raspberry-pi-zero-2-w) |
| Micro-USB Power Plug and Adapter    | Power for Raspberry Pi                                   | \*\*\*                                                                           |
| USB-B (or data) to USB-A Cable      | Connect Raspberry Pi to Power Backup                     | Included with Power Backup                                                       |
| USB-A to Micro-USB OTG Adapter      | Connect Raspberry Pi to Power Backup                     | \*\*\*                                                                           |

---

### Rapsberry Pi Setup

- Set up using [my own guide]().
- Running Trixie OS Lite 32 bit
- Connected the power supply to the RPi via the micro-USB port
- Tested Connection

```bash
lsusb
```

---

### Install NUT

```bash
sudo apt update
sudo apt install nut
```

**1. Open the main NUT config:**

```bash
sudo nano /etc/nut/nut.conf
```

Make sure it contains:

```bash
MODE=standalone
```

Save and exit.

**2. Edit the UPS definition file:**

```bash
sudo nano /etc/nut/ups.conf
```

Add this exact block:

```bash
[apcups]
    driver = usbhid-ups
    port = auto
    desc = "APC Back-UPS Pro 1500"
```

Notes:

port = auto is correct for USB

The name apcups can be anything — we’ll use it consistently

Save and exit.

**3. Edit the user config:**

```bash
sudo nano /etc/nut/upsd.users
```

Add:

```bash
[monuser]
  password = strongpasswordhere
  upsmon master
```

In this case I share the same password as the RPi

Save and exit.

**4. Tell upsmon who to monitor**

```bash
sudo nano /etc/nut/upsmon.conf
```

Find or add:

```bash
MONITOR apcups@localhost 1 monuser strongpasswordhere master
```

Make sure the password matches what you set above.

**5. Start NUT**

Run:

```bash
sudo systemctl restart nut-server
sudo systemctl restart nut-monitor
```

Then check status:

```bash
systemctl status nut-server
```

and

```bash
systemctl status nut-monitor
```

Both should be active (running).

> **Troubleshooting:**
>
> _Can't connect to UPS [apcups] (usbhid-ups-apcups): No such file or directory_:
>
> In my case I needed to disable `maxretry` in `/etc/nut/ups.conf`
>
> _pikachu@pikachu:~ $ sudo upsdrvctl start_
> _Network UPS Tools - UPS driver controller 2.8.1_
> _Network UPS Tools - Generic HID driver 0.52 (2.8.1)_
> _USB communication driver (libusb 1.0) 0.46_
> _libusb1: Could not open any HID devices: insufficient permissions on everything_
> _No matching HID UPS found_
> _upsnotify: notify about state 4 with libsystemd: was requested, but not running as a service unit now, will not spam more about it_
> _upsnotify: failed to notify about state 4: no notification tech defined, will not spam more about it_
> _Driver failed to start (exit status=1)_
>
> Add nut to plugdev:
>
> This is the most important step.
>
> ```bash
> sudo usermod -aG plugdev nut
> ```
>
> Now reboot (this matters — group changes don’t apply until then):
>
> ```bash
> sudo reboot
> ```
>
> After reboot, verify udev rules exist (usually already installed):
>
> ```bash
> ls /lib/udev/rules.d | grep nut
> ```
>
> You should see something like:
>
> ```bash
> 52-nut-usb.rules
> ```
>
> If you see it — great, move on.
>
> If you don’t see it (unlikely, but just in case)
>
> Run:
>
> ```bash
> sudo apt install nut-usb
> ```
>
> Then reboot again.
>
> After reboot, start the driver (again):
>
> ```bash
> sudo upsdrvctl start
> ```
>
> Expected GOOD output
>
> ```bash
> Network UPS Tools - UPS driver controller 2.8.1
> Starting UPS: apcups
> ```

**6. Verify UPS data (the fun part)**

```bash
upsc apcups@localhost
```

You should see a wall of useful data, including things like:

ups.status: OL → On Line power  
battery.charge: 100  
battery.runtime: XXXX  
input.voltage: XXX

This confirms:  
✔ USB comms work  
✔ Driver is correct  
✔ NUT is functioning

---

### Bash Script for Reaction to Loss of Power

Quick push-notification example (using ntfy, simple and free)

1. Install ntfy:

```bash
sudo wget https://github.com/binwiederhier/ntfy/releases/download/v2.15.0/ntfy_2.15.0_linux_armv7.tar.gz
sudo tar zxvf ntfy_2.15.0_linux_armv7.tar.gz
```

2. Install Binaries

```bash
sudo mv ntfy_2.15.0_linux_armv7/ntfy /usr/local/bin/
sudo chmod +x /usr/local/bin/ntfy
```

3. Hooking into NUT

We can configure a simple script that runs whenever the UPS status changes:

Edit the notify config:

```bash
sudo nano /etc/nut/upsmon.conf
```

Find (or add):

```bash
NOTIFYCMD /usr/local/bin/ups-notify.sh

NOTIFYFLAG ONBATT SYSLOG+EXEC
NOTIFYFLAG ONLINE SYSLOG+EXEC
NOTIFYFLAG LOWBATT SYSLOG+EXEC
NOTIFYFLAG SHUTDOWN SYSLOG+EXEC
```

4. Create Script

```bash
sudo nano /usr/local/bin/ups-notify.sh
```

Add code:

**_The code can be found in the file `ups-notify.sh`_**

5. Make the script executable:

```bash
sudo chmod +x /usr/local/bin/ups-notify.sh
```

6. Make the script survive reboots

Sometimes, adding a small systemd override ensures upsdrvctl starts after USB is ready:

```bash
sudo systemctl edit nut-server
```

Add:

```bash
[Unit]
After=network.target usb.target
```

Then:

```bash
sudo systemctl daemon-reexec
sudo systemctl restart nut-server
```

This makes sure the driver is ready before nut-monitor starts.

Confirm upsmon starts on boot

```bash
sudo systemctl enable nut-monitor
```

✅ This ensures your monitor service starts automatically after a reboot.

7. Verify Process

Restart NUT services

```bash
sudo systemctl restart nut-server
sudo systemctl restart nut-monitor
```

Then verify everything is running:

```bash
systemctl status nut-monitor
```

You want to see active (running) with no repeating errors.

Test without pulling the plug (important!)

You can simulate events safely.

Test ONBATT:

```bash
sudo NOTIFYTYPE=ONBATT /usr/local/bin/ups-notify.sh
```

Test ONLINE:

```bash
sudo NOTIFYTYPE=ONLINE /usr/local/bin/ups-notify.sh
```

📱 You should get push notifications immediately.

---

### Set Static IP for Printers

Reserve an IP in your router (recommended)

Most home routers support “DHCP reservation” or “Static lease.”

Steps (general):

Log in to your router’s admin page.

Find the DHCP reservation / LAN IP reservation section.

Locate your Bambu printer in the connected devices list.

Usually shows as “Bambu” or the MAC address printed on the printer or in the network menu.

Assign it a fixed IP (e.g., 192.168.1.42).

Save and reboot the printer if necessary.

### Python Script for Pausing Printers

I have added `config.py` to .gitignore as a way of concealing these variables when I push my changes to GitHub. When doing this from scratch, you will need to create a file called `config.py` and import the variables into `mqtt.py`
