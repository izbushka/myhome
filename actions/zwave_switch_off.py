#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Выключает выключатели света через zwave
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys
import RPi.GPIO as GPIO
import string
import subprocess
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = int(sys.argv[1])

mySensors = mySensors()
sensor = mySensors.getSensor(sensor_id)
zwaveID = str(sensor['sensor'])

if zwaveID:
    subprocess.Popen(['/home/scripts/zwave/zwave-switch.py', zwaveID, '0'])

