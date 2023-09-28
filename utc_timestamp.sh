#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
date -u > Data/utc_timestamp.txt
rclone copy "Data/utc_timestamp.txt" "ALePCardImages:/"
rclone copy "Data/utc_timestamp.txt" "ALePStableData:/"
