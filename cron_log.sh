#!/bin/bash
cd "$(dirname "$0")"
ID=`tail run_before_se.log -n 5000 | grep "Finished: " | tail -n 1 | awk '{print $5}'`
tail run_before_se.log -n 5000 | grep -A 1000 "Started: $ID" | grep -B 1000 "Finished: $ID"
