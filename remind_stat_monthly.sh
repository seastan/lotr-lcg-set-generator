#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 create_mail.py "It's a good time to: 1. Collect RingsDB/DragnCards statistics and make a backup; 2. Check (1) issues on Google Drive" "" > /dev/null
