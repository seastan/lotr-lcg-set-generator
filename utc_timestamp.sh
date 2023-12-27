#!/bin/bash
cd "$(dirname "$0")"
#./env_test.sh || exit
date -u '+%a %d %b %H:%M:%S %Z %Y' > Data/utc_timestamp.txt
rclone copy "Data/utc_timestamp.txt" "ALePCardImages:/"
rclone copy "Data/utc_timestamp.txt" "ALePStableData:/"
