# Simple-dsmr
A simple DSMR to MQTT script

## Hardware Requirements
- Rasberry pi 
- P1 serial cable

## Software requirements
- Basic linux os for Raspberry pi (ex. Raspbian Lite)

## Install required packages:

### pyserial
 `pip install pyserial`

### paho-mqtt
`pip install paho-mqtt`

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

## TO-DO's
- Serial port listener (instead of loop) 
- Adding more DSRM values
- Daemon
- This README