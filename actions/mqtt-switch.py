#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Выключает выключатели света через mqtt
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys
import RPi.GPIO as GPIO
import string
import time
sys.path.append('/home/scripts/libs')
from myMQTT import myMQTT
from myLogs import myLogs

sensor_id = int(sys.argv[1])
state = sys.argv[2]

json = (state[0:1] == '{')
if (state == 'PON' or state == 'POFF' or json):
    #print (str(sensor_id) + " " + state);
    myMQTT = myMQTT()
    myMQTT.connect()
    action = 'ON' if sys.argv[2] == 'PON' or sys.argv[2] == 'ON' else 'OFF';
    if json:
        myMQTT.switchById(sensor_id, state)
    else:
        myMQTT.switchById(sensor_id, action)

    # need some time to finish transaction.
    # Otherwise it still works fine, but "Socket error on client"
    # in mqtt broker log. Doesn't hurt at all. But not nice
    time.sleep(0.05)
    myMQTT.disconnect()
    #print "done"
#elif state[0,1] == '{':

