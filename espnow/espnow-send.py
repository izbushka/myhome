#!/home/scripts/venv/python3/bin/python3

# ./espnow-send.py guestroom control/guestroom/light/1 '{"state": "ON"}'

# Echo server program
import socket,os,struct,time
import sys
import zlib
import time
import random
sys.path.append('/home/scripts/libs')
from mySockets import mySockets
from myESPNOW import myESPNOW

import json

rcpt = sys.argv[1]
topic = sys.argv[2]
msg = sys.argv[3]

rcpt = str(zlib.crc32(rcpt.encode()))

myESPNOW = myESPNOW()
msg = {
    "rcpt": rcpt,
    "ttl": 3,
    "ack": 1,
    "topic": topic,
    "data": msg
}
print(myESPNOW.rawMSG(msg))
mySock = mySockets()
mySock.client('/tmp/espnow.socket');
mySock.client_send(myESPNOW.rawMSG(msg))

#mySock.client_send('<' + rcpt + ';' + sender + ';0;OTA;' + fileCRC32 + ';' + len(binary) + '>')
