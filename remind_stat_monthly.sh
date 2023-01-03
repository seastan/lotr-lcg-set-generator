#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 create_mail.py "It's a good time to collect RingsDB and DragnCards statistics for the previous month and make a backup" "" > /dev/null
