#!/bin/bash
cd "$(dirname "$0")"
if [[ ! $(ps aux | grep ' python3 mail.py' | grep -v grep) ]]; then
  nohup python3 mail.py > /dev/null &
  python3 create_mail.py "Starting LotR Mail Service at $(date)" "" > /dev/null
fi

