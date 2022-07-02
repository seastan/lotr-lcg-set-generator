#!/bin/bash
TIMESTAMP=$(date +%s)
FOLDER="/mnt/volume_postgres/cards/_nightly/$TIMESTAMP"
mkdir -p "$FOLDER"
echo "$FOLDER"