#!/bin/bash
if [[ $(ps aux | grep ' python3 /home/homeassistant/lotr-lcg-set-generator/discord_bot.py' | grep -v grep) ]]; then
  kill `ps aux | grep ' python3 /home/homeassistant/lotr-lcg-set-generator/discord_bot.py' | grep -v grep | awk '{print $2}'`
fi
nohup python3 /home/homeassistant/lotr-lcg-set-generator/discord_bot.py > /dev/null &
