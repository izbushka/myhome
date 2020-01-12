#!/usr/bin/python
# -*- coding: utf-8 -*-
# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries

import sys, os
import subprocess
import string
import datetime
import json

from pprint import pprint
sys.path.append('/home/scripts/libs')
from myLogs import myLogs
from mySensors import mySensors

try:
    import urllib2 as urlreq # Python 2.x
except:
    import urllib.request as urlreq # Python 3.x

class myArduino:
    def __init__(self):
        self.getSensors()

    def closeDB(self): 
        self.mySensors.closeDB();

    def getSensors(self):
        self.sensorsByAddr = {}
        self.sensorsByID = {}
        self.mySensors = mySensors()
        sensors = self.mySensors.getSensors({"type":"arduino"}).values()
        for sensor in sensors:
            if not sensor['sensor'] in self.sensorsByAddr: self.sensorsByAddr[sensor['sensor']] = {} 
            self.sensorsByAddr[sensor['sensor']] = sensor.copy()
            if not sensor['sensor_id'] in self.sensorsByID: self.sensorsByID[sensor['sensor_id']] = {} 
            self.sensorsByID[str(sensor['sensor_id'])] = sensor.copy()
    
    def getSensorByAddr(self, addr):
        try:
            return self.sensorsByAddr[addr]
        except:
            return None

    def getSensorByID(self, id):
        try:
            return self.sensorsByID[str(id)]
        except:
            return None

    def updateSensorByAddr(self, addr, state, commit = False):
        ok = False
        sensor = self.getSensorByAddr(addr)
        if sensor and 'sensor_id' in sensor:
            self.mySensors.saveSensorState(sensor['sensor_id'], state, commit)
            ok = True
        #else: 
            #raise Exception("Sensor '" + addr + "' not found.") 
        return ok

    def commit(self):
        self.mySensors.saveDB()

    def switchByAddr(self, addr, state):
        urlreq.urlopen('http://' + addr + '/' + state.lower())

    def switchById(self, id, state):
        sensor = self.getSensorByID(id);
        if sensor and 'sensor' in sensor:
            addr = sensor['sensor']
            try:
                response = urlreq.urlopen('http://' + addr + '/' + state.lower())
                data = json.loads(response.read())
                if 'states' in data:
                    self.updateSensorByAddr(addr, data['states'][addr], True)
                return data
            except:
                pass
            return None

