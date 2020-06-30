# -*- coding: utf-8 -*-
import httplib2
import json 
import sys
import time
sys.path.append('/home/scripts/libs')
from myConfig import myConfig
from mySensors import mySensors

class myFCM:
    ID = myConfig.get('fcm', 'userId')
    API = myConfig.get('fcm', 'url') 
    errorCounter = 0

    def __init__(self):
        self.SESSION = httplib2.Http()

    def send(self, rcpt, msg):
        dat = msg.copy();
        dat.update({
            'ttl': 1000,
            'priority': 'high',
            'id': self.ID
            });
        to = rcpt.split('=')


        try:
            dat[to[0]] = to[1]
        except IndexError:
            dat['device'] = rcpt
        
        success = False
        while not success and self.errorCounter < 2:
            try:
                response, content = self.SESSION.request(
                        self.API, method="POST",
                        headers={'Content-Type': 'application/json; charset=UTF-8'},
                        body=json.dumps(dat)
                )
                if response.status == 200 and content.decode() == '{}':
                    self.errorCounter = 0;
                    success = True
                else:
                    self.errorCounter += 1
                    time.sleep(1)
            except:
                self.errorCounter += 1
                time.sleep(1)

            if not success:
                fcmSensor = 23
                state = mySensors().getSensor(fcmSensor)
                if state['state'] == 'ON':
                    mySensors().saveSensorState(fcmSensor, 'OFF', True)

        return success
