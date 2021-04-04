#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# Выключает выключатели света через zwave
# Эмуляция проходного выключателя в коридоре
# Старая версия (zwave - zwave) в файле hall-light-loop-switch.py
#
import sys,os,time
import RPi.GPIO as GPIO
import string
import subprocess
import zc.lockfile
sys.path.append('/home/scripts/libs')
from mySensors import mySensors
from myRunLock import myRunLock

sensor_id = int(sys.argv[1]);

lock = myRunLock(str(sensor_id))

mySensors = mySensors()
lightOn = mySensors.getSensor(65)['state'] == 'ON';
if (lightOn):
    subprocess.Popen(['/home/scripts/actions/espnow-switch.py', "65", 'POFF'])
else:
    subprocess.Popen(['/home/scripts/actions/espnow-switch.py', "65", 'PON'])
lock.release()
