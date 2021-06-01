#!/bin/sh
FOLDER=$1
if [ ! -d "$FOLDER" ]; then
  echo "1 No logs folder found"
  exit
fi

DATE=$(date '+%Y-%m-%d')
ERRORS=`grep -s "$DATE" "$FOLDER"/* | grep ERROR | grep -v "echo $DATE" | grep -v "(Scratch)"`

BEFORE_LOG_PATH="$FOLDER/run_before_se_remote.log"
if [ ! -f "$BEFORE_LOG_PATH" ]; then
  echo "2 No Before logs file found"
  echo "$ERRORS"
  exit
fi
ID=`grep "$DATE" "$BEFORE_LOG_PATH" | grep "Finished: " | tail -n 1 | awk '{print $5}'`
if [ ! "$ID" ]; then
  echo "11 No Before script logs for today"
  echo "$ERRORS"
  exit
fi
BEFORE_LOG=`grep "$DATE" "$BEFORE_LOG_PATH" | grep -A 10000 "Started: $ID" | grep -B 10000 "Finished: $ID"`
BEFORE_DONE=`echo "$BEFORE_LOG" | grep "INFO: Done"`
if [ ! "$BEFORE_DONE" ]; then
  echo "12 Before script didn't finish"
  echo "$ERRORS"
  exit
fi
SKIPPING_SE=`echo "$BEFORE_LOG" | grep "No changes since the last run, skipping creating Strange Eons project"`
if [ "$SKIPPING_SE" ]; then
  echo "21 No changes since the last run"
  echo "$ERRORS"
  exit
fi

AFTER_LOG_PATH="$FOLDER/run_after_se_remote.log"
if [ ! -f "$AFTER_LOG_PATH" ]; then
  echo "3 No After logs file found"
  echo "$ERRORS"
  exit
fi
ID=`grep "$DATE" "$AFTER_LOG_PATH" | grep "Finished: " | tail -n 1 | awk '{print $5}'`
if [ ! "$ID" ]; then
  echo "13 No After script logs for today"
  echo "$ERRORS"
  exit
fi
AFTER_LOG=`grep "$DATE" "$AFTER_LOG_PATH" | grep -A 10000 "Started: $ID" | grep -B 10000 "Finished: $ID"`
AFTER_DONE=`echo "$AFTER_LOG" | grep "INFO: Done"`
if [ ! "$AFTER_DONE" ]; then
  echo "14 After script didn't finish"
  echo "$ERRORS"
  exit
fi
echo "22 After script finished successfully"
echo "$ERRORS"
