# -*- coding: utf-8 -*-
import sqlite3
import os
class use(sqlite3.Connection):
    def __init__(self, arg):
        self.currentDB = arg
        os.system("/bin/bash /home/scripts/db/db2ram.sh " + arg)
        db = '/home/ram/db/' + arg + '.sqlite3'
        #print ("INIT!" + db)
        # timeout for "Database locked" (default 5 sec)
        sqlite3.Connection.__init__(self, database=db, timeout=10, check_same_thread=False, isolation_level=None)

        # Allow concurent read and write
        self.cursor().execute('PRAGMA journal_mode=wal')

        self.row_factory = self.show_as_hash

    def show_as_hash(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    def backup_database(self):
        os.system("/bin/bash /home/scripts/db/db2ram.sh " + self.currentDB + ' backup')

