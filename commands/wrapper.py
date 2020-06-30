#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
#
import sys
import RPi.GPIO as GPIO
import string
import subprocess
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = int(sys.argv[1])
cmd = sys.argv[2]

mySensors = mySensors()

newState = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().strip()
newState = str(newState, 'utf-8')

prevState = mySensors.getSensor(sensor_id);
try:
    prevState = prevState['state']
except:
    prevState = 'UNKNOWN'

if not (newState == prevState):
    mySensors.saveSensorState(sensor_id, newState, True)
