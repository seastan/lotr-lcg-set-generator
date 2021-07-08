#!/bin/sh
rclone copy "ALePLogs:/" "$1"
echo "Done"
