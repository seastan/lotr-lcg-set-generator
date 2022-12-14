#!/bin/bash
cd "$(dirname "$0")"
FLAG_FILE="Temp/monitor_discord_changes.txt"
LAST_TIME_RAW=`ls -alst Discord/Changes/ | grep -a '\.json' | tail -1 | awk '{print $7,$8,$9}'`
if [[ "$LAST_TIME_RAW" ]]; then
  LAST_TS=`date -d "$LAST_TIME_RAW" +"%s"`
  CURRENT_TS=`date +"%s"`
  let "DIFF = $CURRENT_TS - $LAST_TS"
  if [ $DIFF -ge 120 ]; then
    if [ ! -f $FLAG_FILE ]; then
      python3 create_mail.py "Discord Changes Monitoring Alert: there are unprocessed JSON files in the queue" "" > /dev/null
      touch $FLAG_FILE
    fi
  else
    rm -rf $FLAG_FILE
  fi
else
  rm -rf $FLAG_FILE
fi
