#!/bin/bash
DATE=$(date +%Y-%m-%d)
rclone copy "$1/Set Folders" "ALePOCTGN:/Backup/$DATE/Set Folders"
rclone copy "$1/Encounter Decks" "ALePOCTGN:/Backup/$DATE/Encounter Decks"
rclone copy "$1/Scratch Set Folders" "ALePOCTGN:/Backup/$DATE/Scratch Set Folders"
rclone copy "$1/Scratch Encounter Decks" "ALePOCTGN:/Backup/$DATE/Scratch Encounter Decks"
