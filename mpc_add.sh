#!/bin/bash
cd "$(dirname "$0")"
DECK="$1"
if [[ ! "$DECK" ]]; then
  echo 'No deck name specified'
  exit 1
fi
flock -x mpc_monitor.lock -c "python3 mpc_monitor.py add \"$DECK\""
