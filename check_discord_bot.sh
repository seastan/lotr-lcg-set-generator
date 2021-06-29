#!/bin/bash
# Setup a cron as:
# * * * * *   <path>/check_discord_bot.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
cd "$(dirname "$0")"
if [[ ! $(ps aux | grep ' python3 discord_bot.py' | grep -v grep) ]]; then
  nohup python3 discord_bot.py > /dev/null &
  python3 create_mail.py "Starting Discord bot at $(date)" "" > /dev/null
fi
