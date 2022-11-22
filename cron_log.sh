#!/bin/bash
cd "$(dirname "$0")"
ID=`tail run_before_se.log -n 50000 | grep -a "Finished: " | tail -n 1 | awk '{print $5}'`
tail run_before_se.log -n 60000 | grep -a -A 10000 "Started: $ID" | grep -a -B 10000 "Finished: $ID"
