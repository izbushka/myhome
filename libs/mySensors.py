#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import syslog
import time
from datetime import datetime

import string
sys.path.append('/home/scripts/libs')
import myDB
from myGraphs import myGraphs

class mySensors:
    def __init__(self):
        self.openDB()
        self.Graphs = None
        self.uncommitedGraph = False

    def openDB(self):
        self.db = myDB.use('sensors')
        self.DB = self.db.cursor()

    def closeDB(self):
        self.saveDB()
        self.db.close();
        if not (self.Graphs is None):
            self.Graphs.closeDB()

    def updateGraphs(self, sensor_id, value, commit = True):
        if self.Graphs is None:
            self.Graphs = myGraphs()
        self.uncommitedGraph = self.Graphs.addData(sensor_id, value) or self.uncommitedGraph;
        if commit:
            self.commitGraphs()

    def commitGraphs(self):
        if self.uncommitedGraph:
            self.Graphs.commit()
            self.uncommitedGraph = False

    def reloadGraphs(self):
        if not (self.Graphs is None):
            self.Graphs.getSensors()

    def getSensorsActions(self):
        self.DB.execute("""
            SELECT sensor_id, sensors.name, type, sensor, delay, runs, repeat_delay, state,
                CASE(actions.enabled) WHEN 'YES' THEN  command ELSE '' END AS command
            FROM sensors
                LEFT JOIN sensors_actions USING(`sensor_id`)
                LEFT JOIN actions USING(`action_id`)
            WHERE sensors.enabled = 'YES'
            ORDER BY sensor_id, run_order
        """)
        _sensors = self.DB.fetchall();
        sensors = {}
        for sensor in _sensors:
            id = sensor['sensor_id']
            if not id in sensors.keys():
                sensors[id] = sensor.copy()
                sensors[id]['command'] = []
            if sensor['command']:
                sensors[id]['command'].append({
                    'on': sensor['state'],
                    'cmd': sensor['command'],
                    'delay': sensor['delay'],
                    'runs': sensor['runs'],
                    'repeat_delay': sensor['repeat_delay']
                })
            if sensor['type'] == 'group':
                grp = sensor['sensor'].split(':')
                sensors[id]['group'] = {
                    'logic': grp[0],
                    'sensors': map(int, grp[1].split(','))
                }
        self.reloadGraphs();
        return sensors.copy()

    def getCommands(self):
        self.DB.execute("""
            SELECT sensor_id, state, updated, sensor, name,
                datetime(updated, 'localtime') as localTime,
                cmd, interval,
                (strftime('%s',CURRENT_TIMESTAMP) - strftime('%s', updated) ) as duration
            FROM sensors
                INNER JOIN commands ON sensor = cmd_id
                LEFT JOIN states USING (sensor_id)
            WHERE enabled = 'YES' AND type='cmd'
        """)
        cmds = {}
        for state in self.DB.fetchall():
            id = state['sensor_id']
            cmds[id] = state.copy()
        return cmds.copy()

    def getSensors(self, extra = ''):
        where = '';
        if extra:
            for field, data in extra.items():
                if isinstance(data, list):
                    where += ' AND `%s` IN (%s) ' % (field, ','.join(map(str,data)))
                else:
                    where += ' AND `%s` = "%s" ' % (field, str(data))

        self.DB.execute("""
            SELECT sensor_id, state, updated, sensor, name, `group`,
                datetime(updated, 'localtime') as localTime,
                (strftime('%s',CURRENT_TIMESTAMP) - strftime('%s', updated) ) as duration
            FROM sensors
                LEFT JOIN states USING(sensor_id)
            WHERE enabled = 'YES'
        """ + where)
        sensorsStates = {}
        for state in self.DB.fetchall():
            id = state['sensor_id']
            sensorsStates[id] = state.copy()
        return sensorsStates.copy()

    def getSensor(self, id):
        state = self.getSensors({'sensor_id': id})
        try:
            return state[int(id)]
        except:
            return {}

    def getSensorState(self, id):
        state = self.getSensors({'sensor_id': id}).values()
        try:
            state = state[0]['state']
        except:
            state = ''
        return state

    def saveSensorState(self, id, state, commit = False, checkPrevState = False):
        # check old state if asked
        if checkPrevState and  state == self.getSensorState(id): return

        updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.DB.execute("""
            UPDATE states
            SET state = '%s', updated = '%s'
            WHERE sensor_id = '%s'
            """ % (state, updated, id));
        if self.DB.rowcount == 0:
            self.DB.execute("""
                INSERT INTO states (sensor_id, state, updated)
                VALUES ('%s', '%s', '%s')
                """ % (id, state, updated));
        sensorsStates = {
            'state': state,
            'sensor_id': id,
            'updated': updated,
            'duration': 0
        }
        self.updateGraphs(id, state, False)
        if commit: 
            self.saveDB()
            self.commitGraphs()
        self.log(" State changed " + str(id) + ' is now ' + state)

        return sensorsStates

    def log(self, data):
        _time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        syslog.syslog(_time + ' ' + str(data))

    def saveDB(self):
        self.db.commit()
        self.commitGraphs()

    def backup(self):
        self.db.commit()
        self.db.backup_database()

    def getLog(self, limit = 100):
        self.DB.execute("""
            SELECT
                `sensor_id`, `state`, `name`, datetime(updated, 'localtime') as updated
            FROM `states_log`
                INNER JOIN `sensors` USING (`sensor_id`)
            ORDER BY `states_log`.`updated` DESC
            LIMIT %d
        """ % limit)
        return self.DB.fetchall();
    ## Loop iteration delay. (decrease CPU load)
    #_delay = 0.3
    #_curTS = int(time.time())
    #if (_speedup): # decrease delay to process queue faster
        #_fastUntill = _curTS + 1 # One next second with low delay

    #if _fastUntill >= _curTS:
        #_delay = 0.05
    #else:
        #_lastNormalSpeed = _curTS

    #if (_curTS - _lastNormalSpeed) > 5:
        #self.log('WARNING! too many jobs in queue!')
        #_delay = 0.5

    #time.sleep(_delay)
