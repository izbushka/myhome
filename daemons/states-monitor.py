#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import os
import time
import syslog
import json

import subprocess
from datetime import datetime

import string
sys.path.append('/home/scripts/libs')
import myDB
from myDaemon import runAsDaemon
from mySensors import mySensors

class StatesMonitor:

    def __init__(self):
        self.mySensors = mySensors()
        self.getSensorsActions()
        self.log("SensorMonitor started")
        self.lastRun = {} #save last action run time (delay)
        self.lastChange = {} # time of last changes
        self.lastCmdRun = {} # time of last run of cmd (not sensor)
        self.sensorsStates = {} # sensors cur state
    
    def log(self, data):
        self.mySensors.log(data)

    def save(self):
        self.mySensors.backup()

    def getSensorsActions(self):
        self.sensors = self.mySensors.getSensorsActions()

    def runAction(self, command, state):
        sensor_id = state['sensor_id']
        if command['on'] == 'BOTH' or state['state'] in command['on'].split(','):
            cmd = '/home/scripts/actions/' + str(command['cmd'])
            if cmd not in self.lastCmdRun:
                self.lastCmdRun[cmd] = 0
            self.log('RUN: Sensor: ' + str(sensor_id) + ' State:' + str(state['state']) + ' LastRun: ' + str(self.lastCmdRun[cmd]) + ' cmd:' + cmd);
            #print (cmd)
            subprocess.Popen([cmd, str(sensor_id), state['state'], state['updated'], str(self.lastCmdRun[cmd])], stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'));
            self.lastCmdRun[cmd] = int(time.time())
        #else:
            #print ("skip cmd as state" + command['on'])

    # update sensors of type 'delay', 'group', 'compare'
    def updateSensorStates(self):
        changed = False
        for id, sensor in self.sensors.items():
            if sensor['type'] == 'group': # sensor type = group
                group = sensor['group']
                grp_state = True if group['logic'] == 'AND' else False
                # перебираем сенсоры группы
                for sensor_id in group['sensors']:
                    inverted = False if sensor_id > 0 else True
                    sensor_id = abs(sensor_id)
                    trueState = 'OFF' if inverted else 'ON'
                    if sensor_id not in self.sensorsStates:
                        grp_state = False
                        break
                    if group['logic'] == 'OR': # логика группы ИЛИ
                        grp_state = self.sensorsStates[sensor_id]['state'] == trueState
                        if grp_state:
                            break
                    elif group['logic'] == 'XOR': # логика группы XOR
                        grp_state = (self.sensorsStates[sensor_id]['state'] == trueState) != grp_state
                    elif group['logic'] == 'AND': # логика группы И
                        grp_state = self.sensorsStates[sensor_id]['state'] == trueState
                        if not grp_state:
                            break
                curState = 'ON' if grp_state else 'OFF'
                if id not in self.sensorsStates or self.sensorsStates[id]['state'] != curState:
                    self.sensorsStates[id] = self.mySensors.saveSensorState(id, curState)
                    changed = True

            elif sensor['type'] == 'delay': # sensor type = delay
                monitorId, monitorState, monitorDelay = sensor['sensor'].split(':')
                monitorId = int(monitorId)
                # monitored sensor state matches wanted state
                if self.sensorsStates[monitorId]['state'] == monitorState:
                    # current sensor state doesn't exist or it's OFF - need to check delay
                    if id not in self.sensorsStates or not self.sensorsStates[id]['state'] == 'ON':
                        format = '%Y-%m-%d %H:%M:%S' if self.sensorsStates[monitorId]['updated'].index('.') < 0 else '%Y-%m-%d %H:%M:%S.%f'
                        updated = datetime.strptime(self.sensorsStates[monitorId]['updated'], format)
                        now = datetime.utcnow()
                        # delay passed
                        if (now - updated).total_seconds() >= int(monitorDelay):
                            if id not in self.sensorsStates or not self.sensorsStates[id]['state'] == 'ON':
                                self.sensorsStates[id] = self.mySensors.saveSensorState(id, 'ON')
                                #print ("update sens 16")
                                changed = True
                        #delay not passed - turning sensor to OFF unless it's already set
                        elif id not in self.sensorsStates or not self.sensorsStates[id]['state'] == 'OFF':
                            self.sensorsStates[id] = self.mySensors.saveSensorState(id, 'OFF')
                            changed = True
                # turning sensor off unless it's already set
                elif id not in self.sensorsStates or not self.sensorsStates[id]['state'] == 'OFF':
                    self.sensorsStates[id] = self.mySensors.saveSensorState(id, 'OFF')
                    changed = True
          
            elif sensor['type'] == 'compare': # sensor type = compare
                rule = json.loads(sensor['sensor'])
                newState = "OFF";
                if rule['id'] in self.sensorsStates: # if target sensor exists. otherwise wait for it to change
                    thatValue = float(self.sensorsStates[rule['id']]['state'])
                    # pick selected logic
                    if rule['logic'] == 'greater':
                        if thatValue > float(rule['value']):
                            newState = "ON"
                            #self.log('greater logic: State ON' + str(thatValue));
                    elif rule['logic'] == 'less':
                        if thatValue < float(rule['value']):
                            newState = "ON"
                    elif rule['logic'] == 'equal':
                        if int(thatValue) == int(float(rule['value'])):
                            newState = "ON"
                    elif rule['logic'] == 'between':
                        if thatValue >= float(rule['min']) and thatValue <= float(rule['max']):
                            newState = "ON"
                    elif rule['logic'] == 'outside':
                        if thatValue < float(rule['min']) or thatValue > float(rule['max']):
                            newState = "ON"
                    # if "compare" sensor changed
                    if id not in self.sensorsStates or newState != self.sensorsStates[id]['state']:
                        self.sensorsStates[id] = self.mySensors.saveSensorState(id, newState)
                        changed = True

        if changed:
            self.mySensors.saveDB()
        return changed

    def main(self):
        _lastNormalSpeed = int(time.time())
        _fastUntill = _lastNormalSpeed - 1
        while True:
            _speedup = False # Flag to decrease loop iteration delay (sleep) after any event (to process queue faster)
            self.sensorsStates = self.mySensors.getSensors()
            _speedup = self.updateSensorStates()
            for id, state in self.sensorsStates.items(): # for each sensor
                if id not in self.lastChange: #for first run
                     self.lastChange[id] = state['updated']
                     self.lastRun[id] = {} # initial value
                if id in self.sensors: #if known (monitored) sensor
                    if not (state['updated'] == self.lastChange[id]): # if changed
                        self.lastRun[id] = {'updated': True} # reset last run time
                        #self.log("DETECTED: Sensor " + str(id) + ' is ' + state['state'] + ' ' + state['updated'])
                        _speedup = True
                    if 'updated' in self.lastRun[id] and self.sensors[id]['command']:
                        runDelay = -1
                        AllActionsDone = True # Flag: Are all actions executed with all delays for this sensor? 
                        for cmd in self.sensors[id]['command']:
                            cmdID = "-".join(str(v) for k,v in sorted(cmd.items()))
                            maxRunDelay = cmd['delay'] + (cmd['runs'] - 1) * cmd['repeat_delay']
                            #self.log('CMDid: ' + cmdID + ' maxDelay ' + str(maxRunDelay) + str(cmd))
                            # max delay reached for this cmd
                            if cmdID in self.lastRun[id] and maxRunDelay <= self.lastRun[id][cmdID]: continue
                            AllActionsDone = False
                            # check for delayed runs
                            for run in range(0, cmd['runs']):
                                runDelay = cmd['delay'] + run * cmd['repeat_delay']
                                # state['duration'] - из базы, округленное до секунды.
                                if ( state['duration'] >= runDelay and 
                                     ( cmdID not in self.lastRun[id] 
                                         or self.lastRun[id][cmdID] < runDelay 
                                     )
                                   ):
                                    self.runAction(cmd, state)
                                    self.lastRun[id][cmdID] = runDelay
                                    #print cmd['cmd']
                                    break #next cmd
                        if (AllActionsDone): # Reset repeat loop untill the next sensor trigger
                            self.lastRun[id] = {}
                self.lastChange[id] = state['updated']

            # Loop iteration delay. (decrease CPU load)
            _delay = 0.2
            _curTS = int(time.time())
            if (_speedup): # decrease delay to process queue faster
                _fastUntill = _curTS + 1 # One next second with low delay

            if _fastUntill >= _curTS: 
                _delay = 0.05
            else: 
                _lastNormalSpeed = _curTS
            
            if (_curTS - _lastNormalSpeed) > 5:
                self.log('WARNING! too many jobs in queue!')
                _delay = 0.5

            time.sleep(_delay)

def _cleanup(signum, frame):
    m.log("exiting on signal" + str(signum))
    m.save()
    quit()

def _reload(signum, frame):
    m.log('Reloading...')
    m.save()
    m.getSensorsActions()

def _start():
    global m
    m = StatesMonitor()
    m.main()

if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)
