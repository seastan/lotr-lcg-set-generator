#!/bin/bash
# Setup a cron as:
# * * * * *   /home/homeassistant/lotr-lcg-set-generator/check_discord_bot.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
if [[ ! $(ps aux | grep ' python3 /home/homeassistant/lotr-lcg-set-generator/discord_bot.py' | grep -v grep) ]]; then
  nohup python3 /home/homeassistant/lotr-lcg-set-generator/discord_bot.py > /dev/null &
  python3 /home/homeassistant/.homeassistant/create_mail.py "Starting Discord bot at $(date)" "" > /dev/null
fi
