#!/usr/bin/python
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
    print "Reloading"

def _start():
    comet = CometClient.CometClient(onMessage) 
    comet.listen(myConfig.get('fcm', 'websocket'))

runAsDaemon(_start, _cleanup, _reload);
#_start()

