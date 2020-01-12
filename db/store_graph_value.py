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

sensor_id = int(sys.argv[1])
sensor_data = sys.argv[2]

db = myDB.use('graphs')
DB = db.cursor()

DB.execute("""
    INSERT INTO `sensors_data` (sensor_id, value)
    VALUES ('%d', '%s')
""" % (sensor_id, sensor_data))
#_sensors = self.DB.fetchall();

db.commit()

#self.db.backup_database()

