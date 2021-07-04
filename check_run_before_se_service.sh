#!/bin/bash
# Setup a cron as:
# * * * * *   <path>/check_run_before_se_service.sh >> <path>/cron.log 2>&1
cd "$(dirname "$0")"
if [[ ! $(ps aux | grep ' python3 run_before_se_service.py' | grep -v grep) ]]; then
  nohup python3 run_before_se_service.py > /dev/null &
  python3 create_mail.py "Starting Cron Service at $(date)" "" > /dev/null
fi
