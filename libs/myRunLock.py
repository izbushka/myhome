# -*- coding: utf-8 -*-
import sys, os
import zc.lockfile
import __main__

class myRunLock():
    def __init__(self, extra = ''):
        caller = os.path.basename(__main__.__file__)
        if extra:
            extra += '.' 
        self.file = '/home/ram/.' + caller + '.' + extra + 'lock'
        try:
            self.lock = zc.lockfile.LockFile(self.file)
        except Exception as e:
            print("Another copy is running. Exiting" + str(e))
            sys.exit()
    def release(self):
        self.lock.close()
        os.remove(self.file)
