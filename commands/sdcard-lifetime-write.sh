#!/bin/bash
GB_WRITED=`awk '{printf "%.1f\n", $1/1000000}' /sys/fs/ext4/mmcblk0p2/lifetime_write_kbytes`
echo $GB_WRITED

#if [ $GB_WRITED -lt 100 ]; then
# /home/scripts/actions/send-telegram.py 94 "SD-Card Lifetime Write: more than 100Gb"
#fi
