#!/home/scripts/venv/python3/bin/python3
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as GPIO
import string
sys.path.append('/home/scripts/libs')
from mySensors import mySensors
from myFCM import myFCM

sensor_id = 98

mySensors = mySensors()

state = mySensors.getSensor(sensor_id);
mySensors.saveSensorState(sensor_id, 'POFF', True)

fcm = myFCM();
data = {
'message': {
    'message': "Kitchen oven is switched OFF",
    'text': "Kitchen oven is switched OFF",
    'cmd': 'showAlert',
    'from': 'raspberry',
    }
}
fcm.send('mirageLG,taniaLG,group=chrome',data);
#fcm.send('mirageLG,taniaLG',data);
