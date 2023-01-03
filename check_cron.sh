#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
if [ $(ls run_before_se.log 2>/dev/null) ]; then
  LOG_RAW=`tail -n 1000 run_before_se.log | grep ' INFO: Done' | tail -n 1 | awk '{print $1,$2}'`
  LOG_TS=`date -d "$LOG_RAW" +"%s"`
  CURRENT_TS=`date +"%s"`
  let "DIFF = $CURRENT_TS - $LOG_TS"
  if [ $DIFF -ge 600 ]; then
    python3 create_mail.py "There are $DIFF seconds since the last Cron activity" "" > /dev/null
  fi
fi
