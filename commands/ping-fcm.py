#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#str(sys.argv)
import sys
import string
import time

sys.path.append('/home/scripts/libs')
from myFCM import myFCM
from myCache import myCache

myCache = myCache()
ok = int(myCache.get('last_fcm_received')) > (time.time() - 90)

fcm = myFCM();
data = {
'message': {
    'message': 'ping',
    'cmd': 'ping',
    'from': 'pi',
    }
}
fcmOk = fcm.send('pi',data); 

print 'ON' if ok and fcmOk else 'OFF'

