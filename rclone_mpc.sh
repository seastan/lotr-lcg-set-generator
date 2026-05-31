#!/bin/bash
FILEPATH=$1
FILENAME="${FILEPATH##*/}"
rclone copy "$FILEPATH" "ALePMakePlayingCards:$FILENAME"
rclone link "ALePMakePlayingCards:$FILENAME"
