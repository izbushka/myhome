#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-

# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries
__version__="0.1.0"

import sys
import os
import time
import syslog

from subprocess import Popen

import string
sys.path.append('/home/scripts/libs')
from myDaemon import runAsDaemon
import myDB
import json

from inspect import getmembers
from pprint import pprint
from mySockets import mySockets
from myZWave import myZWave

myZWave = myZWave();
mySock = mySockets('file')

def _start():
    myZWave.start();
    mySock.server('/tmp/zwave.socket')
    mySock.on_message(handler)

    while True: mySock.serve()

def handler(data):
    obj = json.loads(data)
    if obj['action'] == 'on1':
        myZWave.swon(1)
    elif obj['action'] == 'on2':
        myZWave.swon(2)
    elif obj['action'] == 'off1':
        myZWave.swoff(1)
    elif obj['action'] == 'off2':
        myZWave.swoff(2)
    elif obj['action'] == 'nodeCmd':
        res = myZWave.nodeCmd(obj["id"], obj["method"])
        pprint(getmembers(res))
    elif obj['action'] == 'switch':
        myZWave.switch(obj["id"], obj["state"])

    elif obj['action'] == 'logSwitches':
        myZWave.logSwitches()
    elif obj['action'] == 'logPowerLevels':
        myZWave.logPowerLevels()
    elif obj['action'] == 'logSensors':
        myZWave.logSensors()

    return "ok"

def _cleanup(signum, frame):
    myZWave.stop()
    mySock.close()
    quit()

def _reload(signum, frame):
    print("TODO: Reloading")


if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)

