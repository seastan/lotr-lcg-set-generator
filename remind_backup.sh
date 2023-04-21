#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 create_mail.py "It's a good time to backup Git repos and the Google Drive folder to the local hard drive and the second Google Drive" "" > /dev/null
