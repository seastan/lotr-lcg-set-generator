#!/bin/bash
cd "$(dirname "$0")"
#./env_test.sh || exit  # run anyway
date -u '+%a %d %b %H:%M:%S %Z %Y' > Data/utc_timestamp.txt
if [ "`cat Data/utc_timestamp.txt`" ]; then
  rclone copy "Data/utc_timestamp.txt" "ALePCardImages:/"
  rclone copy "Data/utc_timestamp.txt" "ALePStableData:/"
fi
