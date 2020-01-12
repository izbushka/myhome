#!/home/python-virtualenv/xiaomi/bin/python                                             
# -*- coding: utf-8 -*-
# Xiaomi Mi Home Devices Monitor Library
# WARNING! This script runs under virtualenv (/home/python-virtualenv/)

import sys, os
import subprocess
import string
import datetime
import json
import time

from pprint import pprint
sys.path.append('/home/scripts/libs')
from myLogs import myLogs
from mySensors import mySensors


from miio import AirPurifier
from miio.airpurifier import (
    OperationMode,
    LedBrightness,
    FilterType,
    SleepMode,
    AirPurifierStatus,
    AirPurifierException,
)
from miio.exceptions import DeviceException

try:
    import urllib2 as urlreq # Python 2.x
except:
    import urllib.request as urlreq # Python 3.x

class myMiio:
    def __init__(self):
        try:
            self.mySensors = mySensors()
        except: # reconnect one more time if DB is busy
            time.sleep(2)
            self.mySensors = mySensors()

        self.getDevices()
        self.getSensors()

    def closeDB(self): 
        self.mySensors.closeDB();

    def getDevices(self):
        self.devices = {}
        devices = self.mySensors.getSensors({"type":"miio-device"}).values()
        for device in devices:
            if not device['sensor_id'] in self.devices: self.devices[device['sensor_id']] = {} 
            self.devices[str(device['sensor_id'])] = device.copy()

    def getSensors(self):
        self.sensorsByAddr = {}
        sensors = self.mySensors.getSensors({"type":"miio-sensor"}).values()
        for sensor in sensors:
            if not sensor['sensor'] in self.sensorsByAddr: self.sensorsByAddr[sensor['sensor']] = {} 
            self.sensorsByAddr[sensor['sensor']] = sensor.copy()
    
    def getSensorByDevice(self, device_id, sensor_type):
        sensor_id = str(device_id) + ':' + str(sensor_type);
        try:
            return self.sensorsByAddr[sensor_id]
        except:
            return None

    def updateSensorByDevice(self, device_id, sensor_type, state, commit = False):
        ok = False
        sensor = self.getSensorByDevice(device_id, sensor_type);
        if sensor and 'sensor_id' in sensor:
            if (sensor['state'] != state):
                self.mySensors.saveSensorState(sensor['sensor_id'], state, commit)
            ok = True
        #else: 
            #raise Exception("Sensor '" + addr + "' not found.") 
        return ok

    def updateStates(self):
        for id in self.devices:
            device = self.devices[id]
            if not device: continue
            params = json.loads(device['sensor'])
            if (params['class'] == 'AirPurifier'):
                try:
                    dev = AirPurifier(params['ip'], params['token'])
                    state = str(dev.status())
                    sensors = state.split(' ')
                    for sensor in sensors:
                        sensor = sensor.replace(',','').replace('>', '').split('=')
                        if (len(sensor) == 2):
                            type = sensor[0]
                            value = sensor[1].replace('%','').upper()
                            if type == 'power':
                                if value != device['state']:
                                    self.mySensors.saveSensorState(id, value)
                            elif self.updateSensorByDevice(id, type, value):
                                #print(sensor)
                                pass
                except DeviceException:
                    self.mySensors.saveSensorState(id, 'ERR')
        self.commit()
    def commit(self):
        self.mySensors.saveDB()

