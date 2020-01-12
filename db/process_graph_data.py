#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import syslog
import time
import datetime

import string
sys.path.append('/home/scripts/libs')
import myDB

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
db = myDB.use('graphs')
DB = db.cursor()

def time2sec(time):
    return sum([a*b for a,b in zip([3600,60,1], map(int,time.split(':')))])

def time2interval(time):
    secs = time2sec(time)
    interval = 1800
    intervalN = secs // interval
    intervalW = round(float(secs % interval) / interval, 4)
    #print secs % interval
    #print (str(intervalWeight) + 'ss' + str(secs))
    return [intervalN, intervalW]

def checkIfMidnight():
    now = datetime.datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight < 1800

#DB.execute("SELECT * FROM `sensors_data` ORDER BY `updated`")

DB.execute("SELECT * FROM `sensors`")
sensors = DB.fetchall();
#print(sensors)

now = datetime.datetime.now()
date = yesterday.strftime('%Y-%m-%d') if checkIfMidnight() else now.strftime('%Y-%m-%d')
if len(sys.argv)>1:
    date = sys.argv[1]
    print "USING DATE " + date
for sensor in sensors:
    DB.execute("""
        SELECT *, TIME(`updated`) AS `time`
        FROM `sensors_data`
        WHERE `sensor_id`=%d AND DATE(`updated`)='%s'
        """ % (sensor['sensor_id'], date))
    raw_data = DB.fetchall();

    # create time interval every 30 min (48 valued a day)
    intervalData = range(0, 48)
    for i in range(0, 48): intervalData[i] = 0

    # Previous value
    DB.execute("""
        SELECT `value`
        FROM `week`
        WHERE `sensor_id`=%d AND `date` < '%s'
        ORDER BY `date` desc
        LIMIT 1
        """ % (sensor['sensor_id'], date))
    dbData = DB.fetchall()
    previousValue = dbData[0]['value'] if dbData else 0 # //should be from DB for prev day
    prevValue = previousValue
    prevRawValue = previousValue
    if sensor['data_type'] == 'COUNTER':
        prevRawValue = None

    for raw in raw_data:
        if raw['value'] in ['ON', 'OFF']:
            raw['value'] = int(raw['value'] == 'ON')
        value = round(raw['value'],2);
        if prevRawValue is None:
            prevRawValue = value
        # convert time to 30 min interval
        # N - 30 min interval number starting from 00:00
        # W - time weight in current interval (00:20 has 66% weight in 00 - 00:30 interval)
        [N,W] = time2interval(raw['time'])
        curVal = 0
        # apply data type filter (see README_GRAPHS.TXT)
        if sensor['data_type'] == 'COUNTER':
            value = round(raw['value'] - prevRawValue,2);
            if value < 0: # counter reset
                value = 0
            if not isinstance(intervalData[N], dict):
                curVal = value
            else:
                curVal = intervalData[N]['sum'] + value
        else:
            # Calculate average value for current interval considering data weight
            if not isinstance(intervalData[N], dict): # first value in interval
                # previous value have lasted until this moment: W * prevValue
                curVal = W * prevValue
            else: # already have data in current interval
                curVal = intervalData[N]['sum']
                # appently previous value hasn't lasted to the end of N interval, decreasing sum
                curVal -= (1 - W) * intervalData[N]['value'];
            # suppose current value will last to the end of interval: (1 - W) * value
            curVal += (1 - W) * value;
        # Save current interval data
        intervalData[N] = {
            'value': value,
            'sum': round(curVal, 2)
        }
        prevRawValue = raw['value']
        prevValue = value
    # fill gaps in intervals
    prevValue = 0 if sensor['data_type'] == 'COUNTER' else previousValue
    for N in range(len(intervalData)):
        # if empty interval
        if (intervalData[N] == 0):
            intervalData[N] = {
                'sum': prevValue
            }
        else:
            prevValue = 0 if sensor['data_type'] == 'COUNTER' else intervalData[N]['value']

    DB.execute("""DELETE  FROM `week` WHERE date(`date`) = '%s' AND sensor_id = %d""" % (date, sensor['sensor_id']))
    for N in range(len(intervalData)):
        time = str(datetime.timedelta(seconds=N*1800))
        if (len(time) == 7): #add leading zero
            time = '0' + time
        timestamp = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S')

        #skip future dates
        if timestamp <= now:
            DB.execute("""
                INSERT INTO `week` (`sensor_id`, `value`, `date`)
                VALUES (%d, %f, datetime('%s'))
                """ % (sensor['sensor_id'], float(intervalData[N]['sum']), timestamp))

# Update month and year table            
if checkIfMidnight():
    DB.execute("""DELETE FROM `month` WHERE `date` > '%s'""" % date)
    DB.execute("""
        INSERT INTO `month` 
            SELECT `sensor_id`,  AVG(`value`),
                DATETIME(`date`, '-90 minutes') FROM `week`
            WHERE DATE(`date`) >= '%s'
            GROUP BY `sensor_id`, STRFTIME('%%s',DATE(`date`)),
                (STRFTIME('%%s',date) - STRFTIME('%%s',date(date))) / 7200 
            ORDER BY `sensor_id`, `date`
            """ % date)
    
    DB.execute("""DELETE FROM `year` WHERE `date` > '%s'""" % date)
    DB.execute("""
        INSERT INTO `year` 
            SELECT `sensor_id`,  AVG(`value`),
                DATETIME(`date`, '-210 minutes') FROM `week`
            WHERE DATE(`date`) >= '%s'
            GROUP BY `sensor_id`, STRFTIME('%%s',DATE(`date`)),
                (STRFTIME('%%s',date) - STRFTIME('%%s',date(date))) / 21600
            ORDER BY `sensor_id`, `date`
            """ % date)
    # Delete old data
    old = datetime.datetime.now() - datetime.timedelta(days=15)
    old = old.strftime('%Y-%m-%d')
    DB.execute("""DELETE FROM `week` WHERE `date` < '%s'""" % old)

    old = datetime.datetime.now() - datetime.timedelta(days=62)
    old = old.strftime('%Y-%m-%d')
    DB.execute("""DELETE FROM `month` WHERE `date` < '%s'""" % old)

    old = datetime.datetime.now() - datetime.timedelta(days=732)
    old = old.strftime('%Y-%m-%d')
    DB.execute("""DELETE FROM `year` WHERE `date` < '%s'""" % old)

old = datetime.datetime.now() - datetime.timedelta(days=6)
old = old.strftime('%Y-%m-%d')
DB.execute("""DELETE FROM `sensors_data` WHERE `updated` < '%s'""" % old)

#self.db.backup_database()

db.commit()
