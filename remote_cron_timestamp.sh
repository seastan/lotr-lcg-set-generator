#!/bin/bash
FOLDER="$1"
if [ ! -d "$FOLDER" ]; then
  echo "0"
  exit
fi

LAST_TIMESTAMP=`cat last_remote_cron_timestamp 2>/dev/null`
NEW_TIMESTAMP=`grep " INFO: Done (" "$FOLDER/run_after_se_remote.log" | tail -n 1`

if [ "$LAST_TIMESTAMP" != "$NEW_TIMESTAMP" ]; then
  echo "$NEW_TIMESTAMP" > last_remote_cron_timestamp
  echo "1"
else
  echo "0"
fi
