#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__="0.1.0"

import sys
import os
import time
import syslog
import RPi.GPIO as GPIO
from datetime import datetime

import string
sys.path.append('/home/scripts/libs')
from myDaemon import runAsDaemon
from mySensors import mySensors
import myDB

class SensorMonitor:

    def __init__(self):
        #self.name = os.path.basename(__file__)
        self.mySensors = mySensors()
        self.getSensors()
        self.getSensorGroups()
        self.log("SensorMonitor started")

    def getSensors(self):
        self.sensors = self.mySensors.getSensors({ 'type': 'gpio-in' })
        self.configureGPIO()

    def getSensorGroups(self):
        self.sensorGroups = []
        for id, group in self.mySensors.getSensors({ 'type': 'gpio-group' }).items():
            grp = group['sensor'].split(':')
            group['logic'] = grp[0]
            group['sensors'] = map(int, grp[1].split(','))
            self.sensorGroups.append(group.copy())

    def save(self):
        self.mySensors.backup()

    def configureGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for sensor in self.sensors.values():
            GPIO.setup(int(sensor['sensor']), GPIO.IN, GPIO.PUD_UP)

    def getGPIOState(self, sensor):
        state = GPIO.input(int(sensor['sensor']))
        return 'OFF' if state == GPIO.HIGH else 'ON'

    def log(self, data):
        self.mySensors.log(data)

    def main(self):
        while True:
            #self.logger.info(datetime.now())
            changed = []
            for sensor in self.sensors.values():
                curState = self.getGPIOState(sensor)
                if sensor['state'] != curState:
                    sensor['state'] = curState
                    self.mySensors.saveSensorState(sensor['sensor_id'], sensor['state'])
                    changed.append(sensor['sensor_id'])
            if changed:
                for group in self.sensorGroups:
                    if set(changed).intersection(group['sensors']):
                        grp_state = False if group['logic'] == 'OR' else True
                        # перебираем сенсоры группы
                        for sensor_id in group['sensors']:
                            if group['logic'] == 'OR': # логика группы ИЛИ
                                grp_state = self.sensors[sensor_id]['state'] == 'ON'
                                if grp_state:
                                    break
                            else: # логика группы И
                                grp_state = self.sensors[sensor_id]['state'] == 'ON'
                                if not grp_state:
                                    break
                        curState = 'ON' if grp_state else 'OFF'
                        if group['state'] != curState:
                            group['state'] = curState
                            self.mySensors.saveSensorState(group['sensor_id'], group['state'])
                self.mySensors.saveDB()
            time.sleep(0.3)

def _cleanup(signum, frame):
    m.log("exiting on signal" + str(signum))
    m.save()
    quit()

def _reload(signum, frame):
    m.save()
    m.log('Restarting..')
    m.getSensors()
    m.getSensorGroups()

def _start():
    global m 
    m = SensorMonitor()
    m.main()

runAsDaemon(_start, _cleanup, _reload);
