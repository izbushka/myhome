#!/bin/bash
USAGE=$(/bin/df | /usr/bin/awk '{ if (($5 + 0.01) > 50) print $6 " "  $5 }')

if [ -z "$USAGE" ];
then
    echo "OK"
else 
    echo $USAGE
fi
