#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
DATE=$(date -d '1 days ago' '+%Y-%m-%d')
ERRORS=`grep -s "$DATE" discord_bot.log | grep 'ERROR:' | grep -v 'Discord error:' | grep -v ', stderr:'`
if [ "$ERRORS" ]; then
  python3 create_mail.py "There are errors in the Discord Bot log" "$ERRORS" > /dev/null
fi
