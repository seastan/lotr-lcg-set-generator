#!/bin/sh
ID=`tail /home/homeassistant/lotr-lcg-set-generator/cron.log -n 1000 | grep Finished | tail -n 1 | awk '{print $5}'`
tail /home/homeassistant/lotr-lcg-set-generator/cron.log -n 1000 | grep -A 1000 "Started: $ID" | grep -B 1000 "Finished: $ID"
