#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
HOSTNAME=`cat discord.yaml | grep dragncards_hostname | awk '{print $2}'`
LOG=`ssh $HOSTNAME -i id_rsa '/home/webhost/python/AR/player_cards_stat_monitor.sh'`
if [ ! "$LOG" ]; then
  python3 create_mail.py "No player cards stat cron logs for today" "" > /dev/null
fi
