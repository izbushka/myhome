# -*- coding: utf-8 -*-
import httplib2
import json 
import sys
sys.path.append('/home/scripts/libs')
from myConfig import myConfig

class myFCM:
    ID = myConfig.get('fcm', 'userId')
    API = myConfig.get('fcm', 'url') 

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
        response, content = self.SESSION.request(
                self.API, method="POST",
                headers={'Content-Type': 'application/json; charset=UTF-8'},
                body=json.dumps(dat)
        )
        
        return response.status == 200 and content.decode() == '{}'
