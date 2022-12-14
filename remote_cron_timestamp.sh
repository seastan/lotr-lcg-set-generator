#!/bin/bash
FOLDER="$1"
if [ ! -d "$FOLDER" ]; then
  echo "0"
  exit
fi

TIMESTAMP_FILE="Data/last_remote_cron_timestamp.txt"
LAST_TIMESTAMP=`cat $TIMESTAMP_FILE 2>/dev/null`
NEW_TIMESTAMP=`grep -a " INFO: Done (" "$FOLDER/run_after_se_remote.log" | tail -n 1`

if [ "$LAST_TIMESTAMP" != "$NEW_TIMESTAMP" ]; then
  echo "$NEW_TIMESTAMP" > $TIMESTAMP_FILE
  echo "1"
else
  echo "0"
fi
