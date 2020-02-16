#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
__version__="0.1.0"

import sys
import os
import time
import syslog

from subprocess import Popen

import string
sys.path.append('/home/scripts/libs')
from myDaemon import runAsDaemon
from myConfig import myConfig
import myDB
import CometClient

def onMessage(msg):
    Popen(['/home/scripts/actions/onPushMessageReceived.py', msg])

def _cleanup(signum, frame):
    quit()

def _reload(signum, frame):
    print("Reloading")

def _start():
    comet = CometClient.CometClient(onMessage) 
    comet.listen(myConfig.get('fcm', 'websocket'))


if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)


