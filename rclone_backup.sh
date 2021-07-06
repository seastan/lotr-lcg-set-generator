#!/bin/sh
DATE=$(date +%Y-%m-%d)
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Set Folders" "ALePOCTGN:/Backup/$DATE/Set Folders"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Encounter Decks" "ALePOCTGN:/Backup/$DATE/Encounter Decks"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Scratch Set Folders" "ALePOCTGN:/Backup/$DATE/Scratch Set Folders"
rclone copy "/home/homeassistant/Drive/Playtesting/OCTGN Files/Scratch Encounter Decks" "ALePOCTGN:/Backup/$DATE/Scratch Encounter Decks"
