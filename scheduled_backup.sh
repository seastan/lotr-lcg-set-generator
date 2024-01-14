#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
if [ ! "$1" ]; then
  echo "Error: No folder specified"
  exit 1
fi
python3 scheduled_backup.py "$1"
rclone copy "$1" "ALePLinksBackup:/"
