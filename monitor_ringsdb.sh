#!/bin/bash
# Setup a cron as:
# */10 * * * * /home/homeassistant/lotr-lcg-set-generator/monitor_ringsdb.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
if [[ "$(cat /home/homeassistant/.homeassistant/internet_state)" == "on" ]]; then
  RES=$(curl -s -m 30 "https://ringsdb.com" | grep "The Lord of the Rings: The Card Game Deckbuilder" | wc -l)
  if [[ "$RES" != "1" ]]; then
    python3 /home/homeassistant/.homeassistant/create_mail.py "ringsdb.com is not available" "" > /dev/null
  fi
fi
