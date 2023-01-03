#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
rclone copy "Data/" "ALePCron:/Data/"
rclone copy "Discord/Data/" "ALePCron:/Discord/Data/"
