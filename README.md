# Simple-dsmr
A simple DSMR to MQTT script

## Hardware Requirements
- Rasberry pi 
- P1 serial cable

## Software requirements
- Basic linux os for Raspberry pi (ex. Raspbian Lite)

## Install required packages:

### pyserial
`sudo pip install pyserial`

### paho-mqtt
`sudo pip install paho-mqtt`

## Settings
Copy `config-example.ini` to `config.ini` and fill in the correct data.

### Serial
| Setting | default | Description|  
|:------------- |:----- |:-------------:| 
| baudrate | 115200 | baudrate |
| port | /dev/ttyUSB0 | port on Pi |

### MQTT
| Setting | default | Description|  
|:------------- |:----- |:-------------:| 
| client | p1 | client name |
| broker | - | broker address |
| user | - | broker user |
| password| - | user password |
| topic| dsmr | topic |

## Create Serice
To run the script in the background, and on boot, we need to create a service.

### Create a service

`sudo vi /lib/systemd/system/dsmr.service`

Paste the code and save
```
[Unit]
Description=Simple DSMR Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
WorkingDirectory=/home/pi/dsmr
ExecStart=/usr/bin/python /home/pi/dsmr/read.py
StandardInput=tty-force
StandardOutput=syslog
StandardError=syslog
Restart=on-failure
RestartSec=10
KillMode=process

[Install]
WantedBy=multi-user.target
```
(Update path to file if needed)

### Reload the services

`sudo systemctl daemon-reload`

### Enable the service

`sudo systemctl enable dsmr.service`

### Start the service 

`sudo systemctl start dsmr.service`

### Check service status

`sudo systemctl status dsmr.service`

It should show "Active: active (running)"

## TO-DO's
- Error handling
- Serial port listener (instead of loop) 
- Adding more DSRM values
- Use Daemon instead of Service
- This README