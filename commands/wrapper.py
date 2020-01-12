#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import sys
import RPi.GPIO as GPIO
import string
import subprocess
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = sys.argv[1]
cmd = sys.argv[2]

mySensors = mySensors()

newState = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().strip()

prevState = mySensors.getSensors({'sensor_id': sensor_id}).values();
try:
    prevState = prevState[0]['state']
except:
    prevState = 'UNKNOWN'

if not (newState == prevState):
    mySensors.saveSensorState(sensor_id, newState, True)
