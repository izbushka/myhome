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
from myLogs import myLogs

log = myLogs()

sensor_id = int(sys.argv[1])

mySensors = mySensors()
sensor = mySensors.getSensor(sensor_id)
zwaveID = str(sensor['sensor'])

state = sys.argv[2]

if (state == 'PON' or state == 'POFF' or state == 'ACT' or state == 'TOGGLE'):
    if (state == 'ACT' or state == 'TOGGLE'):
        state = int(sensor['state'] != 'ON')
    else:
        state = int(state == 'PON')
    log.log(str(sensor_id) + ' ' + str(state) + ' ' + zwaveID  +"\n")
    if zwaveID:
        subprocess.Popen(['/home/scripts/zwave/zwave-switch.py', str(zwaveID), str(state)])

