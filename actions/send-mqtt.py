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

sender = sys.argv[1]
topic = sys.argv[2]
payload = sys.argv[3]

myMQTT = myMQTT()
myMQTT.connect()
myMQTT.client.publish(topic, payload)
# in mqtt broker log. Doesn't hurt at all. But not nice
time.sleep(0.05)
myMQTT.disconnect()

