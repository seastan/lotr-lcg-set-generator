#!/bin/bash
cd "$(dirname "$0")"
rclone copy "Data/" "ALePCron:/Data/"
rclone copy "Discord/Data/" "ALePCron:/Discord/Data/"
