#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Выключает выключатели света через ESPNOW
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys
import RPi.GPIO as GPIO
import string
import time
sys.path.append('/home/scripts/libs')
from myESPNOW import myESPNOW
from myLogs import myLogs

sensor_id = int(sys.argv[1])
state = sys.argv[2]

json = (state[0:1] == '{')
if (state == 'PON' or state == 'POFF' or json):
    #print (str(sensor_id) + " " + state);
    myESPNOW = myESPNOW()
    action = 'ON' if sys.argv[2] == 'PON' or sys.argv[2] == 'ON' else 'OFF';
    if json:
        myESPNOW.switchById(sensor_id, state)
    else:
        myESPNOW.switchById(sensor_id, action)

