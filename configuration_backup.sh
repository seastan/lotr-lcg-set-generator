#!/bin/bash
cd "$(dirname "$0")"

FOLDER="$1"
if [ ! -d "$FOLDER" ]; then
  echo "No configuration backup folder found"
  exit
fi

cp configuration.yaml "$FOLDER"
cp discord.yaml "$FOLDER"
cp mpc_monitor.json "$FOLDER"
cp ringsdb_prod_cookies.json "$FOLDER"
cp scheduled_backup.json "$FOLDER"
cp id_rsa "$FOLDER"
