#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
if [[ ! $(ps aux | grep ' python3 discord_bot.py' | grep -v grep) ]]; then
  nohup python3 discord_bot.py > /dev/null &
  python3 create_mail.py "Starting Discord bot at $(date)" "" > /dev/null
fi
