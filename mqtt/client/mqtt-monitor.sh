#!/bin/bash

user=$(grep -A6 '\[mqtt\]' ../../config/config.ini |grep user|cut -d: -f2)
pass=$(grep -A6 '\[mqtt\]' ../../config/config.ini |grep password|cut -d: -f2)
host=$(grep -A6 '\[mqtt\]' ../../config/config.ini |grep host|cut -d: -f2)
port=$(grep -A6 '\[mqtt\]' ../../config/config.ini |grep port|cut -d: -f2)
mosquitto_sub -v -u $user -P $pass -h $host -p $port -t '#'
