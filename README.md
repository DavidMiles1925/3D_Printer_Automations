# 3D Printer Automations

## Introduction

I live in an area where I experience semi-frequent power outages of varying lengths. At one point I had the power go out with 4 printer running simoultaneously, and that prompted me to look into backup power solutions. Battery backups that could keep my printers running for hours were not financially feasible, so I settled for a system that would allow me to pause and gracefully shut down my printers in the event of power outage, greatly increasing the chances of the print surviving the outage.

However, since the system only gives me as little as 10 minutes to shut down my printers, it is very likely that I will miss the power outage if I am in bed, or just outside of the house. I am developing this suite of automations to help detect and automatically react to power outages. I may expand the capabilities further as use cases present themself.

## System Development

### Planned Features

- Load monitoring/response software at Pi startup
  - Set Up Pi OS
  - Connect Pi to Power Backup
  - Write Base Program
- Detect power/battery status
- Detect time remaining on battery
- Upon outage, relay outage status and time remaining message with built in retries
- Upon outage, send pause command to all printers with built in retries
- Upon printers paused, send shutdown command to plugs

### Hadware in Use

| Hardware                            | Link                                                             | Description                                              |
| ----------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------- |
| Tapo Smart Plug (P110M)             | https://www.amazon.com/dp/B0DKG52WQ4                             | Used to control and monitor printer power.               |
| APC Back-UPS Pro 1500VA UPS Battery | https://www.amazon.com/dp/B06VY6FXMM                             | Provides power to printers during an outage.             |
| Raspberry Pi Zero 2 W               | https://www.microcenter.com/product/643085/raspberry-pi-zero-2-w | Used for detection and to control outage reaction logic. |
