#!/bin/bash
cd "$(dirname "$0")"

ENV_FILE="env_health_check.txt"
UUID_FILE="env_uuid.txt"
REMOTE_UUID_FILE="env_uuid_remote.txt"
MAX_DIFF=43200

if [ -f "$ENV_FILE" ]; then
  let "DIFF = `date +%s` - `cat $ENV_FILE`"

  if (( $DIFF > $MAX_DIFF )); then
    if [ -f "$REMOTE_UUID_FILE" ]; then
      exit 0
    fi

    if [[ $(ps aux | grep ' python3 run_before_se_service.py' | grep -v grep) ]]; then
      kill `ps aux | grep ' python3 run_before_se_service.py' | grep -v grep | awk '{print $2}'`
    fi

    if [[ $(ps aux | grep ' python3 discord_bot.py' | grep -v grep) ]]; then
      kill `ps aux | grep ' python3 discord_bot.py' | grep -v grep | awk '{print $2}'`
    fi

    if [ ! -f "$UUID_FILE" ]; then
      python3 create_mail.py "Error: $UUID_FILE not found" "" > /dev/null
      exit 1
    fi

    rclone copyto "ALePCron:/env_uuid.txt" $REMOTE_UUID_FILE || ( python3 create_mail.py "Error: rclone copy from cloud failed" "" > /dev/null; exit 1 )

    if [ ! -f "$REMOTE_UUID_FILE" ]; then
      python3 create_mail.py "Error: rclone copy from cloud failed" "" > /dev/null
      exit 1
    fi

    UUID=`cat $UUID_FILE`
    REMOTE_UUID=`cat $REMOTE_UUID_FILE`

    if [ "$UUID" = "$REMOTE_UUID" ]; then
      if (( `curl -sL -m 15 https://www.google.com | grep google | wc -l` > 0 )); then
        rm -rf $REMOTE_UUID_FILE
        echo `date +%s` > $ENV_FILE
        python3 create_mail.py "Restarting environment $UUID" "" > /dev/null
      fi
    else
      python3 create_mail.py "Environment $UUID is outdated comparing to $REMOTE_UUID" "" > /dev/null
    fi
  else
    if (( `curl -sL -m 15 https://www.google.com | grep google | wc -l` > 0 )); then
      echo `date +%s` > $ENV_FILE
    fi
  fi
else
  if (( `curl -sL -m 15 https://www.google.com | grep google | wc -l` > 0 )); then
    if [ ! -f "$UUID_FILE" ]; then
      echo `cat /proc/sys/kernel/random/uuid` > $UUID_FILE
    fi

    rclone copyto $UUID_FILE "ALePCron:/env_uuid.txt" || ( python3 create_mail.py "Error: rclone copy to cloud failed" "" > /dev/null; exit 1 )
    rm -rf $REMOTE_UUID_FILE
    echo `date +%s` > $ENV_FILE
    UUID=`cat $UUID_FILE`
    python3 create_mail.py "Starting environment $UUID" "" > /dev/null
  fi
fi
