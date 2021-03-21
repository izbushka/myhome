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


class myGraphs:
    def __init__(self):
        self.openDB()
        self.getSensors()

    def openDB(self):
        self.db = myDB.use('graphs')
        self.DB = self.db.cursor()

    def closeDB(self):
        self.DB.close()
        self.db.close()

    def getSensors(self):
        self.DB.execute("""
            SELECT `sensor_id`, `data_type`, `enabled`
            FROM `sensors`
            WHERE `enabled` = 'YES'
        """)
        self.sensors = {}
        for state in self.DB.fetchall():
            id = state['sensor_id']
            self.sensors[id] = state.copy()
        return self.sensors

    def addData(self, id, value, commit = False):
        added = False
        id = int(id)
        if id in self.sensors:
            self.DB.execute("""
                INSERT INTO `sensors_data` (sensor_id, value)
                VALUES ('%d', '%s')
            """ % (id, value))
            added = True
            if commit:
                self.db.commit()
                added = False
        return added

    def commit(self):
        self.db.commit()

