# -*- coding: utf-8 -*-
import sqlite3
import sys
import time
sys.path.append('/home/scripts/libs')
import myDB

class myCache():
    def __init__(self):
        self.openDB()

    def openDB(self):
        self.db = myDB.use('sensors')
        self.DB = self.db.cursor()

    def get(self, key):
        self.DB.execute("SELECT * FROM `memcache` WHERE `key` = '%s' LIMIT 1" % str(key))
        val = self.DB.fetchone()
        if val and (not val['expired'] or val['expired'] >= time.time()): 
            return val['val']
        return None

    def set(self, key, val, exp = 0):
        now = int(time.time());
        if exp > 0:
            exp = now + int(exp);
        self.DB.execute("""
            INSERT OR REPLACE INTO `memcache` 
            VALUES ('%s', '%s', '%d', '%d')
        """ % (key, val, now, exp))
        self.db.commit()
