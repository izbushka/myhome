#!/usr/bin/python
# -*- coding: utf-8 -*-
# Выключает выключатели света через arduino (wifi)
# Аргументы:
# <script_name> sensor_id
# sensor_id - ID сенсора, вызвавшего запуск
#
import sys
import RPi.GPIO as GPIO
import string
sys.path.append('/home/scripts/libs')
from myArduino import myArduino
from myLogs import myLogs

sensor_id = int(sys.argv[1])
state = sys.argv[2]

if (state == 'PON' or state == 'POFF'):
    myArduino = myArduino()
    action = 'on' if sys.argv[2] == 'PON' or sys.argv[2] == 'ON' else 'off';
    myArduino.switchById(sensor_id, action)
