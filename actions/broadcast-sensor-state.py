#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#str(sys.argv)
import sys, os
import string
import time
sys.path.append('/home/scripts/libs')
from myFCM import myFCM
from mySensors import mySensors

if len(sys.argv) > 3: 
    secSinceLastRun = int(time.time()) - int(sys.argv[4])
    if secSinceLastRun < 60: quit()

sensorName = ''
if (sys.argv[1].isdigit()):
    mySensors = mySensors()
    sensorName = mySensors.getSensors({ 'sensor_id': sys.argv[1] }).values()[0]['name'] + ' '; 

args = sys.argv[2:]
#print("/home/scripts/actions/google-assistant-broadcast.sh '" + sensorName + ' is ' +  str(args[0]) + "'")
os.system("/home/scripts/actions/google-assistant-broadcast.sh '" + sensorName + ' is ' +  str(args[0]) + "'")
os.system("echo '" + sensorName + ' is ' +  str(args[0]) + "' | /usr/bin/festival --tts")
