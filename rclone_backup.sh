#!/bin/sh
# Setup a cron as:
# 7 0 * * *   <path>/rclone_backup.sh >> <path>/cron.log 2>&1
DATE=$(date +%Y-%m-%d)
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Set Folders" "ALeP:/Backup/$DATE/Set Folders"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Encounter Decks" "ALeP:/Backup/$DATE/Encounter Decks"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Scratch Set Folders" "ALeP:/Backup/$DATE/Scratch Set Folders"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Scratch Encounter Decks" "ALeP:/Backup/$DATE/Scratch Encounter Decks"
