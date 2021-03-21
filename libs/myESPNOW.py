#!/usr/bin/python
# -*- coding: utf-8 -*-
# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries

import sys
import subprocess
import string
import datetime
import json
import time
import zlib
import serial
import serial.threaded

#from pprint import pprint
sys.path.append('/home/scripts/libs')
from myLogs import myLogs
from mySensors import mySensors
from myConfig import myConfig
from mySockets import mySockets

class myESPNOW(serial.threaded.Protocol):
    masterNodeId = '';
    SOM = '<';
    EOM = '>';

    #password = myConfig.get('espnow', 'password')

    sensorsByAddr = {}
    sensorsById = {}
    sensorsByNodeID = {}

    socket = '/tmp/espnow.socket'
    sender = str(zlib.crc32("master".encode()))

    peers = {}
    pingIntervalSec = 5

    def __init__(self):
        self.getSensors()
        self.socket = None
        self.buffer = ""
        self.started = False
        self.masterNodeId = self.getNodeId("master")

    def __call__(self):
        return self

    def data_received(self, rawData):
        data = rawData.decode('utf-8', errors='ignore').strip('\n');

        if '[dbg]' in data:
            self.log(data)
        #self.log(data)

        for char in data:
            if char == self.EOM and self.started:
                self.started = False
                self.handleMessage(self.buffer)

            elif char == self.SOM:
                self.started = True
                self.buffer = ""
            elif self.started:
                self.buffer += char

    def reload(self):
        self.getSensors()

    def getSensors(self):
        self.sensorsByAddr = {}
        self.sensorsByID = {}
        self.sensorsByNodeID = {}

        sensorsDB = mySensors()
        sensors = sensorsDB.getSensors({"type":"espnow"}).values()
        for sensor in sensors:
            if not sensor['sensor_id'] in self.sensorsByID: self.sensorsByID[sensor['sensor_id']] = {}
            self.sensorsByID[str(sensor['sensor_id'])] = sensor.copy()

            nodeName = self.getNodeId(sensor['sensor'].split('/')[0])
            self.sensorsByNodeID[nodeName] = str(sensor['sensor_id'])
            self.sensorsByAddr[sensor['sensor']] = str(sensor['sensor_id'])

        sensorsDB.closeDB()
        del sensorsDB

    def printNodeIds(self):
        for key in self.sensorsByNodeID:
            sensorId = str(self.sensorsByNodeID[key])
            sensor = self.getSensorByNodeId(key)
            print("name: " + str(sensor["sensor"]) + " NodeID: " + str(key))

    def getSensorByAddr(self, addr):
        try:
            return self.sensorsByID[self.sensorsByAddr[addr]]
        except:
            return None

    def getSensorByNodeId(self, addr):
        try:
            return self.sensorsByID[self.sensorsByNodeID[addr]]
        except:
            return None

    def getSensorByID(self, id):
        try:
            return self.sensorsByID[str(id)]
        except:
            return None

    def getNodeIdName(self, id):
        try:
            if id == self.masterNodeId:
                return 'MASTER'

            sensor = self.sensorsByID[str(self.sensorsByNodeID[id])]
            if sensor and 'sensor_id' in sensor:
                return sensor['sensor'].split('/', 1)[0]

        except Exception as e:
            return id

        return id

    def handleMessage(self, msg):
        data = msg.split(';', 2)
        sender = data[0]
        topic = data[1]
        payload = data[2]
        addr = topic.split('/', 1)

        senderName = self.getNodeIdName(sender)

        self.log("INCOMING>" + senderName + " <" + topic + '> ' + payload)
        if topic == 'ping':
            self.updatePeers(senderName, payload)

        elif topic == 'boot':
            subprocess.Popen(['/home/scripts/actions/send-telegram.py', "debug", senderName, topic, payload]);
        elif topic == 'OTA-RESPONSE':
            with open('/home/ram/espnow-ota.log', 'w') as writer:
                writer.write(payload)
        elif topic == 'MSG-DROPPED':
            self.log("MSG-DROPPED> TODO: Handle this: Node: " + senderName)
        elif len(addr) > 1:
            addr = addr[1]
            if (self.getSensorByAddr(addr)):
                #print(data[1])
                state = json.loads(payload)['state']
                self.updateSensorByAddr(addr, state)

    def updatePeers(self, name, payload):
        self.updatePeer(name, payload)

        curTime = time.time()
        for node in self.peers:
            isOnline = (curTime - self.peers[node]['updated']) < (self.pingIntervalSec * 3)
            if isOnline != self.peers[node]['online']:
                self.peers[node]['online'] = isOnline
                status = "NODE VISIBILITY> " + node + " is " + ("ONLINE" if isOnline else "OFFLINE")
                self.log(status)
                subprocess.Popen(['/home/scripts/actions/send-telegram.py', "debug", status]);

    def updatePeer(self, name, payload):
        curTime = time.time()
        if name in self.peers:
            self.peers[name]['updated'] = curTime
        else:
            self.peers[name] = {
                "updated": curTime,
                "online": False
            }


    def updateSensorByAddr(self, addr, state, commit = True):
        ok = False
        sensor = self.getSensorByAddr(addr)
        self.log(str(addr) + " " + state)
        if sensor and 'sensor_id' in sensor:
            try:
                checkPrevState = 'check' if state == 'ON' or state == 'OFF' else 'not-check';
                subprocess.Popen(['/home/scripts/actions/save_sensor_state.py', str(sensor['sensor_id']), state, checkPrevState]);
                self.log("Switched sensor " + str(sensor['sensor_id']) + " " + state)
            except Exception as e:
                self.log("*** ERROR *** " + str(e))
                pass
            ok = True
        #else:
            #raise Exception("Sensor '" + addr + "' not found.")
        del sensor
        return ok

    def getMsgId(self):
        #milliseconds from midnight
        now = datetime.datetime.now()
        return str(int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() * 1000))

    def getNodeId(self, nodeName):
        return str(zlib.crc32(nodeName.encode()))

    def switchByAddr(self, addr, state):
        topic = "control/" + addr;
        #print (topic + " " + state)
        if state[0:1] != '{': # json
            state = "{\"state\":\"" + state + "\"}"

        #self.client.publish(topic, state)
        mySock = mySockets()
        mySock.client('/tmp/espnow.socket')
        rcpt = self.getNodeId(addr.split('/')[0])
        msg = {
            "rcpt": rcpt,
            "ttl": 3,
            "ack": 1,
            "topic": topic,
            "data": state
        }
        self.log("OUTGOING>>> ESPNOW publish to " + topic + " DATA: " + state)
        #print(self.rawMSG(msg))
        mySock.client_send(self.rawMSG(msg))
        #mySock.client_send('<' + rcpt + ';' + self.sender + ';' + self.getMsgId() + ';' + topic + ';' + state + '>')
        return None

    def switchById(self, id, state):
        sensor = self.getSensorByID(id);
        if sensor and 'sensor' in sensor:
            addr = sensor['sensor']
            return self.switchByAddr(addr, state)

    def onDisconnect(self, client, userdata, rc):
        self.log("--- GOT MQTT DISCONNECT")

    def onConnect(self, client, userdata, flags, rc):
        self.log("+++ MQTT CONNECTED!")

    def log(self, msg):
        logs = myLogs('espnow-serial', 0o666, 1000000)
        logs.log(msg)

    def sign(self, msg):
        return "unsuported"
        #data = (
            #str(msg["rcpt"]) + ';' +
            #str(msg["from"]) + ';' +
            #str(msg["timestamp"]) + ';' +
            #msg["topic"] + ';' +
            #msg["data"] +
            #self.password
            #)
        #return str(zlib.crc32(data.encode()))

    def rawMSG(self, msg):
        return ('<' +
            str(msg["rcpt"]) + ';' +
            str(msg["ack"]) + ';' +
            str(msg["ttl"]) + ';' +
            msg["topic"] + ';' +
            msg["data"] +
            '>')

