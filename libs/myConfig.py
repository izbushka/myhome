# -*- coding: utf-8 -*-

import sys                                                                     
if sys.version_info[0] < 3: 
    import ConfigParser as configparser
else:
    import configparser

class myConfig:
    config = configparser.ConfigParser()
    ready = False

    @staticmethod
    def init(file = '/home/scripts/config/config.ini'):
        myConfig.file = file
        #self.config = configparser.ConfigParser()
        myConfig.config.read(file)
        myConfig.ready = True
    
    @staticmethod
    def get(section, var):
        if(not myConfig.ready):
            myConfig.init()
        return myConfig.config.get(section, var)

