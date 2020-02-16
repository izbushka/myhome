#!/usr/bin/python
# -*- coding: utf-8 -*-
# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries

import sys, os
import subprocess
import string
import datetime
import json
import time

#from pprint import pprint
sys.path.append('/home/scripts/libs')
from myLogs import myLogs
from mySensors import mySensors
import paho.mqtt.client as paho
from myConfig import myConfig

class myMQTT:
    MQTTuser = myConfig.get('mqtt', 'user')
    MQTTpass = myConfig.get('mqtt', 'password')
    MQTTbroker = myConfig.get('mqtt', 'host')
    MQTTport = int(myConfig.get('mqtt', 'port'))

    client = None

    def __init__(self):
        self.getSensors()

    def reload(self):
        self.getSensors()

    def getSensors(self):
        self.sensorsByAddr = {}
        self.sensorsByID = {}
        sensorsDB = mySensors()
        sensors = sensorsDB.getSensors({"type":"mqtt"}).values()
        for sensor in sensors:
            if not sensor['sensor'] in self.sensorsByAddr: self.sensorsByAddr[sensor['sensor']] = {} 
            self.sensorsByAddr[sensor['sensor']] = sensor.copy()
            if not sensor['sensor_id'] in self.sensorsByID: self.sensorsByID[sensor['sensor_id']] = {} 
            self.sensorsByID[str(sensor['sensor_id'])] = sensor.copy()
        sensorsDB.closeDB()

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

    def updateSensorByAddr(self, addr, state, commit = True):
        ok = False
        sensor = self.getSensorByAddr(addr)
        #print(addr + " " + state)
        self.log(str(addr) + " " + state)
        if sensor and 'sensor_id' in sensor:
            try:
                # unable to use self.mySensors - mqtt callback is in another thred
                #print(str(sensor['sensor_id']) + " " + state)
                sensors = mySensors()
                sensors.saveSensorState(sensor['sensor_id'], state, commit)
                sensors.closeDB()
                self.log("Switched sensor " + str(sensor['sensor_id']) + " " + state)
            except Exception as e:
                self.log("*** ERROR *** " + str(e))
                pass
            ok = True
        #else: 
            #raise Exception("Sensor '" + addr + "' not found.") 
        return ok

    def commit(self):
        pass
        #self.mySensors.saveDB()

    def switchByAddr(self, addr, state):
        topic = "control/" + addr;
        #print (topic + " " + state)
        self.log("MQTT publish to " + topic)
        if state[0:1] == '{': # json
            self.client.publish(topic, state)
        else:
            self.client.publish(topic,"{\"state\":\"" + state + "\"}")
        # TODO: MQTT CALL
        #urlreq.urlopen('http://' + addr + '/' + state.lower())

    def switchById(self, id, state):
        sensor = self.getSensorByID(id);
        if sensor and 'sensor' in sensor:
            addr = sensor['sensor']
            self.switchByAddr(addr, state)
            # TODO: MQTT CALL
            #response = urlreq.urlopen('http://' + addr + '/' + state.lower())
            return None
    
    def onDisconnect(self, client, userdata, rc):
        self.log("--- GOT MQTT DISCONNECT")

    def onConnect(self, client, userdata, flags, rc):
        if (self.doSubscribe):
            self.subscribe()
        self.log("+++ MQTT CONNECTED!")

    def onMqttMessage(self, client, userdata, message):
        #print(message.topic + ": message ",str(message.payload.decode("utf-8")))
        topic = message.topic.split('/')
        data  = json.loads(str(message.payload.decode("utf-8")))
        self.log(" GOT MQTT message on " + message.topic + " " + str(message.payload))
        
        if topic[0] == "sensors":
            self.updateSensorByAddr("/".join(topic[1:]), data["state"]);
        elif topic[0] == "lwt":
            host = topic[1]
            for addr in self.sensorsByAddr:
                path = addr.split('/')
                if path[0] == host:
                    sensor = self.sensorsByAddr[addr]
                    if sensor['group'] == 'light-switch':
                        self.updateSensorByAddr(addr, 'ERR');
    
    def log(self, msg):
        logs = myLogs('mqtt-messages')                                                                    
        logs.log(msg)

    def connect(self, subscribe = False):
        self.doSubscribe = subscribe
        self.client = paho.Client("PythonMQTT-" + str(time.time()))
        self.client.username_pw_set(username=self.MQTTuser, password=self.MQTTpass)
        res = self.client.connect(self.MQTTbroker, self.MQTTport)
        self.client.on_message = self.onMqttMessage
        self.client.on_disconnect = self.onDisconnect
        self.client.on_connect = self.onConnect
        self.log(" *** Connecting to MQTT")

    def subscribe(self):
        #self.client.loop_start()
        self.client.subscribe("sensors/#")
        self.client.subscribe("lwt/#")

    def disconnect(self):
        self.log(" *** Disconnecting")
        self.client.disconnect() #disconnect
        self.client.loop_stop() #stop loop

    def loop(self):
        self.client.loop_forever()
#https://stackoverflow.com/questions/36429609/mqtt-paho-python-reliable-reconnect
