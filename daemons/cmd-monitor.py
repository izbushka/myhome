#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import os
import time
import syslog

import subprocess
from datetime import datetime

import string
sys.path.append('/home/scripts/libs')
import myDB
from myDaemon import runAsDaemon
from mySensors import mySensors

class CmdMonitor:

    def __init__(self):
        self.mySensors = mySensors()
        self.sensors = self.mySensors.getCommands()
        self.lastRun = {} #save last action run time (delay)
        self.log("CmdMonitor started")
    
    def log(self, data):
        self.mySensors.log(data)

    def save(self):
        self.mySensors.backup()

    def main(self):
        while True:
            for id, state in self.sensors.items(): # for each sensor
                now = int(time.time())
                if not self.lastRun.has_key(id):
                    # initial value
                    self.lastRun[id] = {'time': now}
                if self.lastRun[id]['time'] + state['interval'] < now:
                    self.lastRun[id]['time'] = now
                    subprocess.Popen(['/home/scripts/commands/wrapper.py', str(id), state['cmd']], stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'));
            # Loop iteration delay. (decrease CPU load)
            time.sleep(2)

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
    m = CmdMonitor()
    m.main()

#_start()
runAsDaemon(_start, _cleanup, _reload);
