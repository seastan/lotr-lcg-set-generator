#!/bin/bash
cd "$(dirname "$0")"
HOSTNAME=`cat discord.yaml | grep dragncards_hostname | awk '{print $2}'`
LOG=`ssh $HOSTNAME '/home/webhost/python/AR/player_cards_stat_monitor.sh'`
if [ ! "$LOG" ]; then
  python3 create_mail.py "No player cards stat cron logs for today" "" > /dev/null
fi
