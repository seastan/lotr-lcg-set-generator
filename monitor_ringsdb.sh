#!/bin/bash
# Setup a cron as:
# */10 * * * * <path>/monitor_ringsdb.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
cd "$(dirname "$0")"
if [[ "$(cat internet_state)" == "on" ]]; then
  RES=$(curl -s -m 30 "https://ringsdb.com" | grep "The Lord of the Rings: The Card Game Deckbuilder" | wc -l)
  if [[ "$RES" != "1" ]]; then
    sleep 60
    RES=$(curl -s -m 30 "https://ringsdb.com" | grep "The Lord of the Rings: The Card Game Deckbuilder" | wc -l)
    if [[ "$RES" != "1" ]]; then
      python3 create_mail.py "ringsdb.com is not available" "" > /dev/null
    fi
  fi
fi
