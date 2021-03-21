#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-
__version__="0.1.0"

import sys
import os
import time
import syslog

from subprocess import Popen
import serial
import serial.threaded

import string
sys.path.append('/home/scripts/libs')
sys.path.append('/home/scripts/libs/python3')
from myDaemon import runAsDaemon
from myLogs import myLogs
from mySockets import mySockets
from myESPNOW import myESPNOW
mySock = mySockets('file')

#class SerialToNet(serial.threaded.Protocol):
    #"""serial->socket"""
    #SOM = '<';
    #EOM = '>';

    #def __init__(self):
        #self.socket = None
        #self.buffer = ""
        #self.started = False
        #self.log = myLogs('espnow-serial', 0o666)

    #def __call__(self):
        #return self

    #def data_received(self, rawData):
        #data = rawData.decode('utf-8', errors='ignore').strip('\n');
        #self.log.log(data)
        #for char in data:
            #if char == self.EOM and self.started:
                #self.started = False
                ##msg = self.buffer.split(';')
                ##ack = '<' + msg[1] + ';' + msg[0] + ';' + 'ACK' + '>' ;
                ##s.write(ack.encode())
                ##print("GOT MESSAGE: " + self.buffer + ' Replying ' + ack)
                ##print(" ***: " + self.buffer)
                #self.log.log("INCOMING>>" + self.buffer)

            #elif char == self.SOM:
                #self.started = True
                #self.buffer = ""
            #elif self.started:
                #self.buffer += char


serialPort = serial.Serial();
serialPort.port = '/dev/ttyUSB1';
serialPort.baudrate = 115200;

def _start():
    if serialPort.isOpen(): serialPort.close()
    serialPort.open();
    
    serial_worker = serial.threaded.ReaderThread(serialPort, myESPNOW())
    serial_worker.start()

    mySock.server(myESPNOW.socket)
    mySock.on_message(handler)

    while True:
        mySock.serve()

def handler(data):
    serialPort.write(data.encode())
    return "ok"

def _cleanup(signum, frame):
    mySock.close()
    if serialPort.isOpen(): serialPort.close()
    quit()

def _reload(signum, frame):
    print("TODO: Reloading")


if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)

