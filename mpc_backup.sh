#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
source env_set.sh

flock -x mpc_monitor.lock -c "python3 mpc_monitor.py backup"
