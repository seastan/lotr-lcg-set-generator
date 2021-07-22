#!/bin/bash
cd "$(dirname "$0")"
DECK="$1"
if [[ ! "$DECK" ]]; then
  echo 'No deck name specified'
  exit 1
fi
flock -x /home/homeassistant/lotr-lcg-set-generator/mpc_monitor.lock -c "python3 /home/homeassistant/lotr-lcg-set-generator/mpc_monitor.py \"$DECK\""
echo 'Done'
