#!/bin/bash
DB=$1
ACTION=$2

if [ "$DB" = "help" ]
then
    echo "Usage: db2ram.sh <DB NAME> <ACTION>"
    echo " Actions:"
    echo "   replace: disk -> ram"
    echo "   backup: ram -> disk"
    echo "   no args: init ram disk"
    exit
fi
DB="${DB/.sqlite3/}"

ramPath='/home/ram/db'
sdPath='/home/db/sqlite'
sdFile=$sdPath/${DB}.sqlite3
ramFile=$ramPath/${DB}.sqlite3
LOCK='/var/lock/db2ram.sh.lock'
[ -d $ramPath ] || mkdir $ramPath

if [ ! -f $ramFile ] || [ "$ACTION" = "replace" ]
then
    exec {lock_fd}>$LOCK || exit 1
    while ! flock -n "$lock_fd"; do sleep 1; done
    /bin/cp $sdFile $ramFile
    chmod 777 $ramPath 
    chmod 666 $ramFile
else
    i=0
    while [ -f $LOCK ] && [ "$i" -lt 60 ]; do ((i++)); sleep 1; done
fi


if [ "$ACTION" = "backup" ]
then
    sqlite3 $ramFile vacuum
    sqlite3 $ramFile ".backup $sdFile"
fi

[ -f $LOCK ] && rm $LOCK
