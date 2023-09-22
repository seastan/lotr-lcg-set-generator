#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 monitor_mpc_url_format.py
