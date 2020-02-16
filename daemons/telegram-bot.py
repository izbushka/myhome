#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-

# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries
__version__="0.1.0"

import sys
import os
import time
import syslog

import threading
import queue

import string
sys.path.append('/home/scripts/libs')
sys.path.append('/home/scripts/libs/python3')
from myDaemon import runAsDaemon
import json

from mySockets import mySockets
from myTelegram import myTelegram

myTelegram = myTelegram()
myTelegram.setTimeout(60)

#def _start():
    #myTelegram.startBot()

def _cleanup(signum, frame):
    #thread_obj.start()
    #mySock.close()
    #myTelegram.stop()
    #thread_obj.stop() #stop thread
    quit()

def _reload(signum, frame):
    print("TODO: Reloading")

#_start()
#runAsDaemon(_start, _cleanup, _reload);
runAsDaemon(myTelegram.start, _cleanup, _reload);

