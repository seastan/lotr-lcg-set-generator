#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 scheduled_backup.py "$1"
rclone copy "$1" "ALePLinksBackup:/"
