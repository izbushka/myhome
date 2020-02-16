#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-

__version__="0.1.0"

import sys
import os
import time
import syslog

import string
sys.path.append('/home/scripts/libs')
from myDaemon import runAsDaemon

from mySockets import mySockets
from myMQTT import myMQTT
from myLogs import myLogs
import json


client = myMQTT()
def _start():
    client.reload()
    client.connect(True)
    client.loop()
    client.disconnect()

def _cleanup(signum, frame):
    client.disconnect()
    quit()

def _reload(signum, frame):
    client.reload()


if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)
