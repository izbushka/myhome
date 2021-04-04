#!/home/scripts/venv/python3/bin/python3
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

sensors = mySensors.getSensors({"group":"light-switch"}).values()
for sensor in sensors:
    if sensor['state'] != 'OFF':
        mySensors.saveSensorState(sensor['sensor_id'], 'POFF', True)
        time.sleep(2)
