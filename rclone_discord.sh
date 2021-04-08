#!/bin/sh
# Setup a cron as:
# 27 * * * *  /home/homeassistant/lotr-lcg-set-generator/rclone_discord.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
rclone copy "/home/homeassistant/lotr-lcg-set-generator/Discord" "ALeP:/Discord"
