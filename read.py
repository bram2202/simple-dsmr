#!/usr/bin/python
import sys
import os
import time
import serial
import re
import datetime
import paho.mqtt.client as mqtt
import ConfigParser

print("start")
debug = 0

# Configs
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

mqtt_client = Config.get('mqtt', 'client')
mqtt_broker_address = Config.get('mqtt', 'broker')
mqtt_username = Config.get('mqtt', 'user')
mqtt_password = Config.get('mqtt', 'password')
mqtt_topic = Config.get('mqtt','topic')

# Setup Serial
ser = serial.Serial()
ser.baudrate = Config.get('serial', 'baudrate')
ser.port = Config.get('serial', 'port')
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20


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
    client.publish(mqtt_topic + "/status", "OK")  # Send status msg
except Exception as e:
    print(e)
    sys.exit()

while(1):
    # Reading P1
    power_tariff = None           # 96.14.0
    power_consuption = None       # 1.7.0  (kW)    
    total_consuption_low = None   # 1.8.1  (kWh, tariff 1)
    total_consuption_high = None  # 1.8.2  (kWh, tariff 2)
    power_production = None       # 2.7.0  (kW)
    total_production_low = None   # 2.8.1  (kWh, tariff 1)
    total_production_high = None  # 2.8.2  (kWh, tariff 2)
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
            if debug == 1:
                print(p1_line)  # Debug
        except:
            break

    # Parse line to useble values
    for ii, line in enumerate(lines[:]):
        if ":96.14.0(" in line:  #0-0:96.14.0(0001)
            power_tariff = int(re.search("[0-9]-[0-9]:96.14.0\([0]{3,}(.*)\)", line).group(1))
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
            total_production_high = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:2.8.2\([0]{1,}(.*)\*kWh\)", line).group(1))))
        elif ":1.7.0" in line:
            power_consuption = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:1.7.0\([0]{1,}(.*)\*kW\)", line).group(1))))
        elif ":2.7.0" in line:
            power_production = float("{0:.2f}".format(
                float(re.search("[0-9]-[0-9]:2.7.0\([0]{1,}(.*)\*kW\)", line).group(1))))
        elif ":24.2.1" in line:
            total_gas = float("{0:.2f}".format(float(re.search(
                "[0-9]-[0-9]:24.2.1\([0-9]{1,}(.*)W\)\([0-9]{1,1}(.*)\*m3\)", line).group(2))))

    # Debug prints
    if debug == 1:
        print("---")
        print(power_tariff)
        print(power_consuption)
        print(power_production)
        print(total_consuption_low)
        print(total_consuption_high)
        print(total_production_low)
        print(total_production_high)
        print(total_gas)
        print("---")

    # Send data over MQTT
    if power_tariff != None:
        client.publish(mqtt_topic + "/power_tariff", power_tariff)

    if power_consuption != None:
        client.publish(mqtt_topic + "/power_consuption", power_consuption)

    if power_production != None:
        client.publish(mqtt_topic + "/power_production", power_production)

    if total_consuption_low != None:
        client.publish(mqtt_topic + "/total_consuption_low", total_consuption_low)

    if total_consuption_high != None:
        client.publish(mqtt_topic + "/total_consuption_high", total_consuption_high)

    if total_production_low != None:
        client.publish(mqtt_topic + "/total_production_low", total_production_low)

    if total_production_high != None:
        client.publish(mqtt_topic + "/total_production_high", total_production_high)

    if total_gas != None:
        client.publish(mqtt_topic + "/total_gas", total_gas)

print("end")
ser.close()