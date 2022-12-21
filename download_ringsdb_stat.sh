#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 download_ringsdb_stat.py
