#!/bin/bash
cd "$(dirname "$0")"
flock -xn mpc_monitor.lock -c 'python3 mpc_monitor.py > /dev/null'
