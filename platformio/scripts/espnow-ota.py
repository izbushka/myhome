#!/home/scripts/venv/python3/bin/python3

# Echo server program
import socket,os,struct,time
import sys
import zlib
import time
sys.path.append('/home/scripts/libs')
from mySockets import mySockets

import json
import re
import base64

startTime = time.time()

otaLog = "/home/ram/espnow-ota.log"
# TODO: to config
topic = 'OTA'

def cleanLog():
    file = open(otaLog, "w")
    file.write('')
    file.close()

def sign(msg):
    return ""

def rawMSG(msg):
    return ('<' +
        str(msg["rcpt"]) + ';'
        + str(msg["ack"]) + ';'
        + str(msg["ttl"]) + ';'
        + msg["topic"] + ';'
        + msg["data"]
        + '>')    

class NeedResend():
    lastRepeatId = 0
    def __call__(self):
        try:
            file = open(otaLog, "r")
            lastMatch = ''
            for line in file:
                 if re.search('.*repeat', line):
                     lastMatch = line
            file.close()
            if len(lastMatch):
                data=json.loads(lastMatch)
                if "repeat" in data:
                    repeatId = int(data['repeat'])
                    #if self.lastRepeatId != repeatId:
                        #self.lastRepeatId = repeatId
                    cleanLog()
                    time.sleep(3)
                    return repeatId

            return 0
        except Exception as e:
            print("EXEPTION", e, lastMatch)
            return 0
    
cleanLog()
needResend = NeedResend()

class ConfirmDone():
    lastRepeatId = 0
    def __call__(self):
        try:
            file = open(otaLog, "r")
            lastMatch = ''
            for line in file:
                if re.search('.*complete', line):
                    lastMatch = "complete"
                    print("Update completed")
                if re.search('.*canceled', line):
                    lastMatch = "canceled"
                    print("Update canceled: " + line)
            file.close()
            return lastMatch
        except Exception as e:
            print("EXEPTION", e, lastMatch)
            return ''
confirmDone = ConfirmDone()

rcpt = "slave"
fileS = ""
startChunk = 0

if len(sys.argv) > 1:
    rcpt = sys.argv[1]
if len(sys.argv) > 2:
    fileS = sys.argv[2]
if len(sys.argv) > 3:
    startChunk = int(sys.argv[3])

rcpt = str(zlib.crc32(rcpt.encode()))
#print(rcpt)

sender = str(zlib.crc32("master".encode()))
msgSize = 160
msgSize = 128
encoded = ""

if not fileS or not os.path.exists(fileS):
    print("Usage: <script> nodeName otaFile.bin")
    sys.exit()

#fileS = '/home/mirage/tmp/split/60k'
#fileS = '/home/mirage/tmp/split/200ac'
#fileS = '/home/git/platformio/ota-updates/test1.bin'
#fileS = '/home/git/platformio/ota-updates/espnow-raw.bin'
#fileS = '/home/git/platformio/ota-updates/espnow-raw-repeater.bin'
#fileS = '/home/scripts/test1.bin'
#fileS = '/home/scripts/guestroom.bin'
#fileS = '/home/scripts/cabinet.bin'
#fileS = '/home/scripts/smallhall.bin'
with open(fileS, "rb") as f:
    binary = f.read();

fileCRC32 = str(zlib.crc32(binary));

chunks = [binary[i:i+msgSize] for i in range(0, len(binary), msgSize)]

if not startChunk:
    print("Sending ERASE request, waiting for complete...")
    mySock = mySockets()
    msg = {
        "rcpt": rcpt,
        "ttl": 3,
        "ack": 0,
        "topic": topic,
        "data": '0' + ';' + str(len(binary)) + ';' + fileCRC32
    }
    print (rawMSG(msg))
    mySock.client('/tmp/espnow.socket')
    mySock.client_send(rawMSG(msg))

    erased = False
    while not erased:
        with open(otaLog) as file:
            data = file.read()
            if re.search('.*"erased"', data):
                erased = True
            else: 
                time.sleep(1)
                
packets = len(chunks)

id = startChunk
#id=1740
while id < packets:

    encodedChunk = base64.b64encode(chunks[id]).decode('ascii')
    msg = {
        "rcpt": rcpt,
        "ttl": 3,
        "ack": 0,
        "topic": topic,
        "data": str(id+1) + ';' + encodedChunk
    }
    #continue
    mySock = mySockets()
    mySock.client('/tmp/espnow.socket')
    mySock.client_send(rawMSG(msg))

    if id % 20 == 0:
        time.sleep(0.2)
        print("Sending " + str(round(id / packets * 100, 1)) + '% Last message id:' + str(id+1));
        repeat = needResend()
        if repeat > 0:
            id = repeat - 2
            print("RESENDING DATA FROM " + str(repeat))
    else:
        time.sleep(0.05)
    id += 1
    if id == packets:
        time.sleep(1)
        repeat = needResend()
        if repeat > 0:
            id = repeat - 2
            continue

mySock = mySockets()
mySock.client('/tmp/espnow.socket')
#msg = '<' + rcpt + ';' + sender + ';' + str(len(chunks)+1) + ';OTA;***COMPLETE***>';
msg = {
    "rcpt": rcpt,
    "sender": sender,
    "id": 0,
    "topic": topic,
    "ttl": 3,
    "timestamp": int(time.time()),
    "ack": 0,
    "data": str(len(chunks)+1) + ';***COMPLETE***'
}
msg["id"] = sign(msg)

print("Sending " + rawMSG(msg));
mySock.client_send(rawMSG(msg))


endTime = time.time()
print("Duration: ", endTime - startTime)
#print(reverse)
#f = open("result.bin", "ab")
#f.write(base64.b64decode(reverse))
#f.close()
#print(encoded)
#mySock.client_send(msg)
sys.exit()

