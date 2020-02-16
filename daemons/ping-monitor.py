#!/home/scripts/venv/python3/bin/python3
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
import myDB

class PingMonitor:
    def openDB(self):
        self.db = myDB.use('sensors')
        self.DB = self.db.cursor()

    def getSensors(self):
        self.DB.execute("""
            SELECT sensor_id, sensor, name, state, updated
            FROM sensors
                LEFT JOIN states USING(`sensor_id`)
            WHERE type = 'ping' AND enabled = 'YES'
        """)
        
        sensors = self.DB.fetchall();
        self.sensors = {}
        for sensor in sensors:
            id = sensor['sensor_id']
            self.sensors[id] = sensor.copy()

    def saveSensorState(self, sensor):
        self.DB.execute("""
            UPDATE states
            SET state = '%s', updated = strftime('%%Y-%%m-%%d %%H:%%M:%%f')
            WHERE sensor_id = '%s'
            """ % (sensor['state'], sensor['sensor_id']));
        if self.DB.rowcount == 0:
            self.DB.execute("""
                INSERT INTO states (sensor_id, state)
                VALUES ('%s', '%s')
                """ % (sensor['sensor_id'], sensor['state']));

    def init(self):
        #self.name = os.path.basename(__file__)
        self.openDB()
        self.getSensors()
        self.log("SensorMonitor started")

    def log(self, data):
        syslog.syslog(str(data))

    def main(self):
        self.init()
        while True:
            self.getSensors()
            #self.logger.info(datetime.now())
            processes = {}
            for sensor in self.sensors.values():
                processes[sensor['sensor_id']] = Popen(['ping', '-n', '-w5', '-c3', sensor['sensor']], stdout=open('/dev/null', 'w'))

            changed = False
            while processes:
                for id, proc in processes.items():
                    if proc.poll() is not None: # ping finished
                        del processes[id] # remove from the process list
                        curState = 'OFF'
                        if proc.returncode == 0:
                            curState = 'ON'
                        elif proc.returncode > 0: # 1 - host down, 2 - host network unreachable
                            curState = 'OFF'
                        #else:
                            #print('%s error' % ip)
                        if self.sensors[id]['state'] != curState:
                            self.sensors[id]['state'] = curState
                            sensor = self.sensors[id]
                            #print (str(id) + ' ' + curState + ' ' + sensor['sensor'])
                            self.saveSensorState(sensor)
                            changed = True
                            self.log('State Changed: ' + sensor['name'] + ' ' + str(sensor['sensor_id']) +  '->' + curState);

                        break
            timeout = 30
            if changed:
                self.db.commit()
                timeout = 5
            time.sleep(timeout)

def _cleanup(signum, frame):
    m.log("exiting on signal" + str(signum))
    m.db.commit()
    quit()

def _reload(signum, frame):
    m.db.commit()
    m.getSensors()

def _start():
    global m
    m = PingMonitor()
    m.main()

if len(sys.argv) > 1 and sys.argv[1] == 'no-daemon':
    _start()
else:
    runAsDaemon(_start, _cleanup, _reload)

