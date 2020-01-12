#!/home/python-openzwave/bin/python
# -*- coding: utf-8 -*-

# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries

# Echo server program
import sys
import time
import string
import json
import logging
import os
from inspect import getmembers
from pprint import pprint
sys.path.append('/home/scripts/libs')

from mySockets import mySockets
from myZWave import myZWave

logger = logging.getLogger("jsocket.example_servers")
myZWave = myZWave();



def handler(data):
    obj = json.loads(data)
    logger.info(obj)
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


#mySock = mySockets('net')
mySock = mySockets('file')
mySock.server('/tmp/zwave.socket')
os.chmod('/tmp/zwave.socket', 666)
mySock.on_message(handler)

try:
    while True: mySock.serve()
except:
    logger.info('Server is being stopped, please wait...')
    myZWave.stop()
    mySock.close()

