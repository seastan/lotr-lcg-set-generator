#!/bin/bash
rclone copy "$1" "ALePOCTGN:/Set Folders"
rclone copy "$2" "ALePOCTGN:/Encounter Decks"
echo "Done"
