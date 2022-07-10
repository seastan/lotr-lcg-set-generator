#!/bin/bash
grep "$(date '+%Y-%m-%d') " /home/webhost/python/AR/player_cards_stat_cron.log | grep 'INFO: Done ' | tail -1
