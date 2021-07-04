#!/bin/bash
# Setup a cron as:
# 5,15,25,35,45,55 * * * * <path>/monitor_testringsdb.sh >> <path>/cron.log 2>&1
cd "$(dirname "$0")"
if [[ "$(cat internet_state 2>/dev/null)" != "off" ]]; then
  RES=$(curl -s -m 30 "https://test.ringsdb.com" | grep "The Lord of the Rings: The Card Game Deckbuilder" | wc -l)
  if [[ "$RES" != "1" ]]; then
    sleep 60
    RES=$(curl -s -m 30 "https://test.ringsdb.com" | grep "The Lord of the Rings: The Card Game Deckbuilder" | wc -l)
    if [[ "$RES" != "1" ]]; then
      python3 create_mail.py "test.ringsdb.com is not available" "" > /dev/null
    fi
  fi
fi
