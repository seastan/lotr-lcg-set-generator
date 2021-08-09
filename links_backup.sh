#!/bin/bash
cd "$(dirname "$0")"
python3 links_backup.py "$1"
rclone copy "$1" "ALePLinksBackup:/"
