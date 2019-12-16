#!/usr/bin/python
import sys
import os
import time
import serial
import re
import datetime
import paho.mqtt.client as mqtt

print("start")

mqtt_client = "p1"
mqtt_broker_address = "<IP address>"
mqtt_username = "<username>"
mqtt_password = "<password>"

ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20
ser.port = "/dev/ttyUSB0"

# Setup perial
try:
    ser.open()
except Exception as e:
    print(e)
    sys.exit()

# Setup MQTT
try:
    client = mqtt.Client(mqtt_client)  # Create new instance
    # Set username and password
    client.username_pw_set(mqtt_username, mqtt_password)
    client.connect(mqtt_broker_address)  # Connect to broker
    client.publish("dsmr/status", "OK")  # Send status msg
except Exception as e:
    print(e)
    sys.exit()

while(1):
    # Reading P1
    power_consuption = None       # 1.7.0 (kW)
    power_production = None       # 2.7.0 (kW)
    total_production_low = None   # 2.8.1 (kWh, tariff 1)
    total_production_high = None  # 2.8.2 (kWh, tariff 2)
    total_consuption_low = None   # 1.8.1 (kWh, tariff 1)
    total_consuption_high = None  # 1.8.2 (kWh, tariff 2)
    total_gas = None              # 24.2.1 (m3)

    # Read serial
    i = 0
    lines = []
    while i < 25:
        p1_line = ''
        try:
            p1_raw = ser.readline()
        except:
            sys.exit("Error while reading serial")
        try:
            p1_str = str(p1_raw)
            p1_line = p1_str.strip()
            lines.append(p1_line)
            i = i + 1
            print(p1_line)  # Debug
        except:
            break

    # Parse line to useble values
    for ii, line in enumerate(lines[:]):
        if ":1.8.1(" in line:
            total_consuption_low = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:1.8.1\([0]{1,}(.*)\*kWh\)", line).group(1))))
        elif ":1.8.2(" in line:
            total_consuption_high = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:1.8.2\([0]{1,}(.*)\*kWh\)", line).group(1))))
        elif ":2.8.1(" in line:
            total_production_low = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:2.8.1\([0]{1,}(.*)\*kWh\)", line).group(1))))
        elif ":2.8.2(" in line:
            total_consuption_high = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:2.8.2\([0]{1,}(.*)\*kWh\)", line).group(1))))
        elif ":1.7.0" in line:
            power_consuption = float("{0:.3f}".format(
                float(re.search("[0-9]-[0-9]:1.7.0\([0]{1,}(.*)\*kW\)", line).group(1))))
        elif ":2.7.0" in line:
            power_production = float("{0:.3f}".format(
                float(re.search("[0-9]-[0-9]:2.7.0\([0]{1,}(.*)\*kW\)", line).group(1))))
        elif ":24.2.1" in line:
            total_gas = float("{0:.3f}".format(float(re.search(
                "[0-9]-[0-9]:24.2.1\([0-9]{1,}(.*)W\)\([0-9]{1,1}(.*)\*m3\)", line).group(2))))

    # Debug prints
    print("---")
    print(power_consuption)
    print(power_production)
    print(total_consuption_low)
    print(total_consuption_high)
    print(total_production_low)
    print(total_consuption_high)
    print(total_gas)
    print("---")

    # Send data over MQTT
    if power_consuption != None:
        client.publish("dsmr/power_consuption", power_consuption)

    if power_production != None:
        client.publish("dsmr/power_production", power_production)

    if total_consuption_low != None:
        client.publish("dsmr/total_consuption_low", total_consuption_low)

    if total_consuption_high != None:
        client.publish("dsmr/total_consuption_high", total_consuption_high)

    if total_production_low != None:
        client.publish("dsmr/total_production_low", total_production_low)

    if total_consuption_high != None:
        client.publish("dsmr/total_consuption_high", total_consuption_high)

    if total_gas != None:
        client.publish("dsmr/total_gas", total_gas)

print("end")
ser.close()