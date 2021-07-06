#!/bin/sh
# Setup a cron as:
# 27 * * * *  <path>/rclone_discord.sh >> <path>/cron.log 2>&1
cd "$(dirname "$0")"
rclone copy "Discord" "ALePOCTGN:/Discord"
