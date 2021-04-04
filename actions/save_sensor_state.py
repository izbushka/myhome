#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Сохраняет состояние сенсора в базе 
# Аргументы:
# <script_name> sensor_id state
# sensor_id - ID сенсора
# state - состояние sensor_id

import sys
import RPi.GPIO as GPIO
import string
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = int(sys.argv[1])
state = sys.argv[2]
checkState = False
if len(sys.argv) > 3:            
  checkState= sys.argv[3] == 'check'

mySensors = mySensors()
mySensors.saveSensorState(sensor_id, state, True, checkState)
