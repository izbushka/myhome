# -*- coding: utf-8 -*-
import sys
import os
import daemon
import daemon.pidlockfile
import daemon.runner
import syslog
import signal
import shutil
import lockfile
import string
import subprocess
from datetime import datetime


#def prepareDaemonContext():
def getDaemonContext(program_cleanup, program_reload):
    scriptName = os.path.basename(sys.argv[0])

    subprocess.Popen(['/home/scripts/actions/send-fcm.py', 'send', scriptName, 'started'],  stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'));

    lockFile = '/var/run/' + scriptName + '.pid'
    pid = os.getpid()
    pidfile=daemon.pidlockfile.TimeoutPIDLockFile(lockFile, acquire_timeout=2)
    if os.path.isfile((lockFile + '.lock')) and not os.path.isfile(lockFile):
        os.remove(lockFile + '.lock')

    context = daemon.DaemonContext()
    context.working_directory = os.path.dirname(os.path.realpath(__file__))
    context.detach_process = True

    filename = "/home/ram/" + scriptName + ".log"
    if os.path.isfile(filename):
        if os.path.isfile(filename + '.old'):
            subprocess.Popen(['/home/scripts/actions/send-telegram-textfile.py', filename + '.old'],  stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'));
        shutil.copy(filename, filename + '.old')

    error_log = open(filename, "w+", 1)
    context.stdout = error_log
    context.stderr = error_log

    # Check for stale pid file
    if daemon.runner.is_pidfile_stale(pidfile):
        pidfile.break_lock()
    # Setup PID file
    context.pidfile = pidfile

    context.signal_map = {
        signal.SIGHUP: program_reload,
        signal.SIGQUIT: program_cleanup,
        signal.SIGINT: program_cleanup,
        signal.SIGTERM: program_cleanup,
    }

    return context

def runAsDaemon(_start, program_cleanup, program_reload):
    try:
        print("Starting..")
        with getDaemonContext(program_cleanup, program_reload):
            print (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " Starting..")
            _start()
    except lockfile.LockTimeout:
        syslog.syslog("Another copy is running. Exiting")

