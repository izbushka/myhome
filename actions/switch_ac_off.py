#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as GPIO
import string
import json
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = int(sys.argv[1])

mySensors = mySensors()

state = mySensors.getSensor(sensor_id);
acState = json.loads(state['state'])
acState['state'] = 'off';

mySensors.saveSensorState(sensor_id, json.dumps(acState, separators=(',', ':')), True)
