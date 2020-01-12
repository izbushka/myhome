#!/usr/bin/python
# -*- coding: utf-8 -*-
# Выключает выключатели света через zwave
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys, time
import RPi.GPIO as GPIO
import string
import subprocess
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

mySensors = mySensors()

sensors = mySensors.getSensors({"type":"zwave"}).values()
for sensor in sensors:
    if sensor['state'] == 'ON' and sensor['group'] == 'light-switch':
        zwaveID = str(sensor['sensor'])
        subprocess.Popen(['/home/scripts/zwave/zwave-switch.py', zwaveID, '0'])
        time.sleep(2)

sensors = mySensors.getSensors({"type":"arduino"}).values()
for sensor in sensors:
    if sensor['state'] == 'ON' and sensor['group'] == 'light-switch':
        subprocess.Popen(['/home/scripts/actions/arduino-switch.py', str(sensor['sensor_id']), 'POFF'])
        time.sleep(2)

sensors = mySensors.getSensors({"type":"mqtt"}).values()
for sensor in sensors:
    if sensor['state'] == 'ON' and sensor['group'] == 'light-switch':
        subprocess.Popen(['/home/scripts/actions/mqtt-switch.py', str(sensor['sensor_id']), 'POFF'])
        time.sleep(2)

