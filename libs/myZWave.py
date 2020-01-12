#!/home/python-openzwave/bin/python
# -*- coding: utf-8 -*-
# WARNING! This script runs under virtualenv (/home/python-openzwave/)
# it has it's own libriries

import sys, os
import subprocess
import string
import datetime

import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
import six
if six.PY3:
    from pydispatch import dispatcher
else:
    from louie import dispatcher

from pprint import pprint
sys.path.append('/home/scripts/libs')
from myLogs import myLogs

class myZWave:
    def __init__(self):
        self.lastReport = {}
        self.startTime = time.time()

    def setup(self):
        self.logs = myLogs('zwave-daemon')

        device="/dev/ttyUSB0"
        log="Info" # Debug

        #Define some manager options
        # see docs at the end of file
        options = ZWaveOption(device, \
          #config_path="openzwave/config", \
          user_path="/home/scripts/zwave/home",\
          cmd_line=""
        )
        #options.set_log_file("OZW_Log.log")
        options.set_append_log_file(False)
        options.set_console_output(False)
        options.set_save_log_level('None')
        #options.set_queue_log_level("None")
        #options.set_save_log_level('Info')
        options.set_logging(False)
        options.lock()

        self.ZWave = ZWaveNetwork(options, log=None, autostart=False)

    def start(self):
        self.setup()
        #self.ZWave.controller.soft_reset();
        #self.logs.log("continue");
        #sys.exit(1);

        dispatcher.connect(self.louie_network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
        dispatcher.connect(self.louie_network_resetted, ZWaveNetwork.SIGNAL_NETWORK_RESETTED)
        dispatcher.connect(self.louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

        self.ZWave.start()

        for i in range(0,300):
            if self.ZWave.state>=self.ZWave.STATE_STARTED:
                self.logs.log("Startup time: " + str(self.getRunTime()))
                break
            else:
                self.logs.log("***** STARTING *****")
                #sys.stdout.write(".")
                #sys.stdout.write("starting.")
                #sys.stdout.flush()
                time.sleep(1.0)
        if self.ZWave.state<self.ZWave.STATE_STARTED:
            self.logs.log(".")
            self.logs.log("Can't initialise driver! Look at the logs in OZW_Log.log. Runtime: " + str(self.getRunTime()))
            sys.exit(1)

        for i in range(0,600):
            #if self.ZWave.state>=self.ZWave.STATE_AWAKED: # wait fot awaked nodes only:
            if self.ZWave.state>=self.ZWave.STATE_READY:
                self.logs.log("Got ready by " + str(self.getRunTime()))
                break
            else:
                time.sleep(1.0)
        if not self.ZWave.is_ready:
        #if self.ZWave.state < self.ZWave.STATE_AWAKED:
            self.logs.log("Runtime: " + str(self.getRunTime()))
            self.logs.log("Can't start network! Look at the logs in OZW_Log.log")
            self.logs.log("Resetting controller in 5 sec. Then reinit")
            self.ZWave.controller.soft_reset();
            sys.exit(1)

        self.logs.log("Collecting switches...")
        self.collectSwitches()

    def getRunTime(self):
        return (time.time() - self.startTime)
    def stop(self):
        self.ZWave.stop()
        self.logs.log("####### STOPPED ######")

    def nodeCmd(self, id, cmd):
        return getattr(self.ZWave.nodes[id], cmd)()
    def nodeProp(self, id, cmd):
        return getattr(self.ZWave.nodes[id], cmd)

    def switch(self, id, state):
        try:
            node = self.switches[str(id)];
            self.logs.log('Switching node ' + str(node) + ' sw: ' + str(id) + ' to ' + str(state))
            newState = True if state == 1 else False
            self.ZWave.nodes[int(node)].set_switch(int(id), newState)
        except:
            e = sys.exc_info()[0]
            self.logs.log("UNKNOWN SWITCH: " + str(id) + ' Error:' + str(e))
        #self.ZWave.nodes[2].set_switch(216172782152138752, True)


    def collectSwitches(self):
        self.switches = {}
        for node in self.ZWave.nodes:
            for val in self.ZWave.nodes[node].get_switches():
                self.switches[str(val)] = node
                self.logs.log("* Found switch " + str(val) + ' on node ' + str(node))
        self.logs.log(self.switches)

    def logSwitches(self):
        self.logs.log("** List of Swithces ** ")
        self.logs.log(self.switches)

    def logPowerLevels(self):
        _nodes = {}
        for node in self.ZWave.nodes:
            for val in self.ZWave.nodes[node].get_power_levels():
                _nodes[str(val)] = node
        self.logs.log("** List of PowerLevels ** ")
        self.logs.log(_nodes)

    def logSensors(self):
        _nodes = {}
        for node in self.ZWave.nodes:
            for val in self.ZWave.nodes[node].get_sensors():
                _nodes[str(val)] = node
        self.logs.log("** List of Sensors ** ")
        self.logs.log(_nodes)

    # Event Listeners
    def louie_network_started(self):
        self.logs.log('//////////// ZWave network is started ////////////')
        self.logs.log('Louie signal : OpenZWave network is started : homeid {:08x} - {} nodes were found.'.format(self.ZWave.home_id, self.ZWave.nodes_count))
        #self.ZWave.controller.soft_reset();

    def louie_network_resetted(self):
        #self.logs.log('Louie signal : OpenZWave network is resetted.')
        pass

    def louie_network_ready(self):
        self.logs.log('//////////// ZWave network is ready ////////////')
        self.logs.log('Louie signal : ZWave network is ready : {} nodes were found.'.format(self.ZWave.nodes_count))
        self.logs.log('Louie signal : Controller : {}'.format(self.ZWave.controller))
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE)
        dispatcher.connect(self.louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
        dispatcher.connect(self.louie_ctrl_message, ZWaveController.SIGNAL_CONTROLLER)

        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE_READY)
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE_REMOVED)
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_SCENE_EVENT)
        dispatcher.connect(self.louie_my_update, ZWaveNetwork.SIGNAL_NOTIFICATION)
        dispatcher.connect(self.louie_my_update, ZWaveNetwork.SIGNAL_VALUE_REFRESHED)

    def louie_node_update(self,network, node):
        #self.logs.log('Louie signal : Node update : {}.'.format(node))
        pass

    def louie_my_update(self,network, node= False, t = False, f = False):
        self.logs.log('Louie signal : Node update : {}.'.format(node))

    def louie_value_update(self, network, node, value):
        now = datetime.datetime.now()
        log = str(now) + 'Value update: {}.'.format(value)
        #if value.data == False and value.value_id != 216172782152138752:
            #self.ZWave.nodes[2].set_switch(216172782152138752, False)
        cmd = '/home/scripts/zwave/event-handler.py'
        state = str(value.data)
        zwaveID = str(value.value_id)
        if (
                zwaveID not in self.lastReport
                or self.lastReport[zwaveID]['val'] != state
                or (time.time() - self.lastReport[zwaveID]['time']) > 2
           ):
            self.lastReport[zwaveID] = { 'time': time.time(), 'val': state }
            subprocess.Popen([cmd, str(value.value_id), state], stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'));
            self.logs.log(log + " ☉")
        else:
            self.logs.log(log)




    def louie_ctrl_message(self, state, message, network, controller):
        #self.logs.log('Louie signal : Controller message : {}.'.format(message))
        pass


#mz = myZWave();
#mz.stop();

#sw 1
#network.nodes[2].set_switch(216172782152138752,False)
#sw2


#----------------------------------------
#        CONFIGURATION OPTIONS
#----------------------------------------
#{
  #"AppendLogFile": {
    #"type": "Bool",
    #"doc": "Append new session logs to existing log file (false = overwrite)."
  #},
  #"Associate": {
    #"type": "Bool",
    #"doc": "Enable automatic association of the controller with group one of every device."
  #},
  #"AssumeAwake": {
    #"type": "Bool",
    #"doc": "Assume Devices that Support the Wakeup CC are awake when we first query them ..."
  #},
  #"ConfigPath": {
    #"type": "String",
    #"doc": "Path to the OpenZWave config folder."
  #},
  #"ConsoleOutput": {
    #"type": "Bool",
    #"doc": "Display log information on console (as well as save to disk)."
  #},
  #"CustomSecuredCC": {
    #"type": "String",
    #"doc": "What List of Custom CC should we always encrypt if SecurityStrategy is CUSTOM.",
    #"value": "0x62,0x4c,0x63"
  #},
  #"DriverMaxAttempts": {
    #"type": "Int",
    #"doc": "."
  #},
  #"DumpTriggerLevel": {
    #"type": "Int",
    #"doc": "Default is to never dump RAM-stored log messages."
  #},
  #"EnableSIS": {
    #"type": "Bool",
    #"doc": "Automatically become a SUC if there is no SUC on the network."
  #},
  #"EnforceSecureReception": {
    #"type": "Bool",
    #"doc": "If we recieve a clear text message for a CC that is Secured, should we drop the message"
  #},
  #"Exclude": {
    #"type": "String",
    #"doc": "Remove support for the listed command classes."
  #},
  #"Include": {
    #"type": "String",
    #"doc": "Only handle the specified command classes. The Exclude option is ignored if anything is listed here."
  #},
  #"Interface": {
    #"type": "String",
    #"doc": "Identify the serial port to be accessed (TODO: change the code so more than one serial port can be specified and HID)."
  #},
  #"IntervalBetweenPolls": {
    #"type": "Bool",
    #"doc": "If false, try to execute the entire poll list within the PollInterval time frame. If true, wait for PollInterval milliseconds between polls."
  #},
  #"LogFileName": {
    #"type": "String",
    #"doc": "Name of the log file (can be changed via Log::SetLogFileName)."
  #},
  #"Logging": {
    #"type": "Bool",
    #"doc": "Enable logging of library activity."
  #},
  #"NetworkKey": {
    #"type": "String",
    #"doc": "Key used to negotiate and communicate with devices that support Security Command Class"
  #},
  #"NotifyOnDriverUnload": {
    #"type": "Bool",
    #"doc": "Should we send the Node/Value Notifications on Driver Unloading - Read comments in Driver::~Driver() method about possible race conditions."
  #},
  #"NotifyTransactions": {
    #"type": "Bool",
    #"doc": "Notifications when transaction complete is reported."
  #},
  #"PerformReturnRoutes": {
    #"type": "Bool",
    #"doc": "If true, return routes will be updated."
  #},
  #"PollInterval": {
    #"type": "Int",
    #"doc": "30 seconds (can easily poll 30 values in this time; ~120 values is the effective limit for 30 seconds)."
  #},
  #"QueueLogLevel": {
    #"type": "Int",
    #"doc": "Save (in RAM) log messages equal to or above LogLevel_Debug."
  #},
  #"RefreshAllUserCodes": {
    #"type": "Bool",
    #"doc": "If true, during startup, we refresh all the UserCodes the device reports it supports. If False, we stop after we get the first Available slot (Some devices have 250+ usercode slots! - That makes our Session Stage Very Long )."
  #},
  #"RetryTimeout": {
    #"type": "Int",
    #"doc": "How long do we wait to timeout messages sent."
  #},
  #"SaveConfiguration": {
    #"type": "Bool",
    #"doc": "Save the XML configuration upon driver close."
  #},
  #"SaveLogLevel": {
    #"type": "Int",
    #"doc": "Save (to file) log messages equal to or above LogLevel_Detail."
  #},
  #"SecurityStrategy": {
    #"type": "String",
    #"doc": "Should we encrypt CCs that are available via both clear text and Security CC?.",
    #"value": "SUPPORTED"
  #},
  #"SuppressValueRefresh": {
    #"type": "Bool",
    #"doc": "If true, notifications for refreshed (but unchanged) values will not be sent."
  #},
  #"UserPath": {
    #"type": "String",
    #"doc": "Path to the users data folder."
  #}
#}
