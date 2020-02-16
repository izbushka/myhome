#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Переключает состояние сенсора в базе
# Аргументы:
# <script_name> sensor_id state
# sensor_id - ID сенсора, вызвавшего запуск
# state - состояние sensor_id
#
import sys
import RPi.GPIO as GPIO
import string
sys.path.append('/home/scripts/libs')
from mySensors import mySensors

sensor_id = sys.argv[1]
state = sys.argv[2]

mySensors = mySensors()

dbState = mySensors.getSensorState(sensor_id)
if dbState != state:
    mySensors.saveSensorState(sensor_id, state, True)
