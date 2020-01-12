#!/usr/bin/python
# -*- coding: utf-8 -*-
# Выключает выключатели света через mqtt
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys
import RPi.GPIO as GPIO
import string
sys.path.append('/home/scripts/libs')
from myMQTT import myMQTT
from myLogs import myLogs

sensor_id = int(sys.argv[1])
state = sys.argv[2]

json = (state[0:1] == '{')
if (state == 'PON' or state == 'POFF' or json):
    print (str(sensor_id) + " " + state);
    myMQTT = myMQTT()
    myMQTT.connect()
    action = 'ON' if sys.argv[2] == 'PON' or sys.argv[2] == 'ON' else 'OFF';
    if json:
        myMQTT.switchById(sensor_id, state)
    else:
        myMQTT.switchById(sensor_id, action)
    #print "done"
#elif state[0,1] == '{':

