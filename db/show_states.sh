#!/bin/bash
sqlite3 /home/ram/db/sensors.sqlite3 -header "select sensor_id as id, datetime(updated, 'localtime') as localTime, state, name, (strftime('%s',CURRENT_TIMESTAMP) - strftime('%s', updated) )/60 as duration, sensor from states inner join sensors using(sensor_id) where enabled='YES' order by name;"
#sqlite3 /home/ram/db/sensors.sqlite3 -header ".width 2 20 2 20 10; select sensor_id as id, datetime(updated, 'localtime') as localTime, state, name, (strftime('%s',CURRENT_TIMESTAMP) - strftime('%s', updated) )/60 as duration from states inner join sensors using(sensor_id) where enabled='YES' order by updated;"

#sqlite3 /home/ram/db/sensors.sqlite3 "select sensor_id, datetime(updated, 'localtime') as localTime, state, name from sensors LEFT JOIN states using(sensor_id) order by updated;"
