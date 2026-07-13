#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
source env_set.sh

python3 create_mail.py "It's a good time to: 1. collect monthly statistics and make a backup; 2. check (1) issues on Google Drive; 3. review conditional formatting in the spreadsheet" "" > /dev/null
