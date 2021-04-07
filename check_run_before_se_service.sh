#!/bin/bash
# Setup a cron as:
# * * * * *   /home/homeassistant/lotr-lcg-set-generator/check_run_before_se_service.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
if [[ ! $(ps aux | grep ' python3 /home/homeassistant/lotr-lcg-set-generator/run_before_se_service.py' | grep -v grep) ]]; then
  nohup python3 /home/homeassistant/lotr-lcg-set-generator/run_before_se_service.py > /dev/null &
  python3 /home/homeassistant/.homeassistant/create_mail.py "Starting Cron Service at $(date)" "" > /dev/null
fi
