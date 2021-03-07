#!/bin/sh
# Setup a cron as:
# 7 0 * * *   /home/homeassistant/lotr-lcg-set-generator/rclone_backup.sh >> /home/homeassistant/.homeassistant/cron.log 2>&1
DATE=$(date +%Y-%m-%d)
rclone copy "/home/homeassistant/Drive/OCTGN Files/Set Folders" "ALeP:/Backup/$DATE/Set Folders"
rclone copy "/home/homeassistant/Drive/OCTGN Files/Encounter Decks" "ALeP:/Backup/$DATE/Encounter Decks"
rclone copy "/home/homeassistant/Drive/OCTGN Files/Scratch Set Folders" "ALeP:/Backup/$DATE/Scratch Set Folders"
rclone copy "/home/homeassistant/Drive/OCTGN Files/Scratch Encounter Decks" "ALeP:/Backup/$DATE/Scratch Encounter Decks"
