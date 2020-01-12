#!/bin/bash
#Forse WiFi to disconnect and reconnect than
/usr/bin/sudo /sbin/wpa_cli disconnect
/bin/sleep 5
/usr/bin/sudo /sbin/wpa_cli reconnect

/bin/sleep 10
# Notify mirage
date=`date`
/home/scripts/actions/send-fcm.py 23 "Wifi Reconnected $date"
