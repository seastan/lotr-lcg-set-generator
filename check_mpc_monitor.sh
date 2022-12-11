#!/bin/bash
cd "$(dirname "$0")"
if [ $(ls mpc_monitor.log 2>/dev/null) ]; then
  LOG_RAW=`tail -n 1000 mpc_monitor.log | grep ' INFO: Finished' | tail -n 1 | awk '{print $1,$2}'`
  LOG_TS=`date -d "$LOG_RAW" +"%s"`
  CURRENT_TS=`date +"%s"`
  let "DIFF = $CURRENT_TS - $LOG_TS"
  if [ $DIFF -ge 1800 ]; then
    python3 create_mail.py "There are $DIFF seconds since the last MPC Monitor activity" "" > /dev/null
  fi
fi
