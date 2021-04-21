#!/bin/sh
# Setup a cron as:
# 0 8 * * 1   /home/homeassistant/lotr-lcg-set-generator/remind_art_backup.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
python3 /home/homeassistant/.homeassistant/create_mail.py "It's a good time to backup ALeP CardImages folder" "" > /dev/null
