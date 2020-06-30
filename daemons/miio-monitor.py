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
from myMiio import myMiio
from myLogs import myLogs
import json

def _start():
    miio = myMiio()
    while True:
        miio.getDevices()
        miio.updateStates()
        miio.commit()
        time.sleep(60)

def _cleanup(signum, frame):
    quit()

def _reload(signum, frame):
    #Nothing to do, it creates a copy every time. This is TODO
    pass


if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)

