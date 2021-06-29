#!/bin/sh
# Setup a cron as:
# 0 8 * * 1   <path>/remind_art_backup.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
cd "$(dirname "$0")"
python3 create_mail.py "It's a good time to backup ALeP CardImages folder" "" > /dev/null
