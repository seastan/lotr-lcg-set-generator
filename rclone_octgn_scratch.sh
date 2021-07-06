#!/bin/sh
rclone copy "$1" "ALePOCTGN:/Scratch Set Folders"
rclone copy "$2" "ALePOCTGN:/Scratch Encounter Decks"
echo "Done"
