# -*- coding: utf-8 -*-
import sys, os
from datetime import datetime
sys.path.append('/home/scripts/libs')
import myDB

class myLogs():

    def __init__(self, filename = 'myLog', perm = 0o644):
        self.filename = '/home/ram/' + filename + '.log'
        self.openLog(perm)

    def openLog(self, perm = 0o644):
        self.file = open(self.filename, 'a')
        try:
            os.chmod(self.filename, perm)
        except:
            pass

    def log(self, data):
        if (os.path.getsize(self.filename) > 100000):
            self.closeLog()
            os.rename(self.filename, self.filename + '.old')
            self.openLog()
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + '> ' + str(data) + "\n"
        try:
            self.file.write(data);
            self.file.flush();
        except Exception as e:
            self.openLog()
            self.file.write("** myLogs: log write error: " + str(e) + ". Reopening log and repeating last message:\n");
            try:
                self.file.write(data);
                self.file.flush();
            except:
                pass
        #TODO: try unbuffered stdout:
        #sys.stdout.flush()

    def closeLog(self):
        self.file.close();
