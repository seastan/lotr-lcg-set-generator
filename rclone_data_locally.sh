#!/bin/bash
cd "$(dirname "$0")"
rclone copy "ALePCron:/Data/" "Data/"
rclone copy "ALePCron:/Discord/Data/" "Discord/Data/"
