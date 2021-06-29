#!/bin/bash
cd "$(dirname "$0")"
if [[ $(ps aux | grep ' python3 discord_bot.py' | grep -v grep) ]]; then
  kill `ps aux | grep ' python3 discord_bot.py' | grep -v grep | awk '{print $2}'`
fi
nohup python3 discord_bot.py > /dev/null &
