#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
autoCloseTime = [['9:00', '21:00']]
autoOffTimer = 9000; # seconds


import sys
import RPi.GPIO as GPIO
import string
import json
import subprocess
from datetime import datetime

sys.path.append('/home/scripts/libs')
from mySensors import mySensors

rightTime = False
curtime = datetime.now()
for period in autoCloseTime:
    h,m = period[0].split(':');
    start = curtime.replace(hour=int(h), minute=int(m), second=0);
    h,m = period[1].split(':');
    end = curtime.replace(hour=int(h), minute=int(m), second=0);
    if (start <= curtime and curtime < end):
        rightTime = True;
        break
if (not rightTime):
    exit()

sensor_id = int(sys.argv[1])
mySensors = mySensors()
state = mySensors.getSensor(sensor_id);
acState = json.loads(state['state'])

if (acState['state'] == 'off' or state['duration'] < autoOffTimer):
    exit()

subprocess.Popen(['/home/scripts/actions/switch_ac_off.py', str(sensor_id), 'OFF']);
