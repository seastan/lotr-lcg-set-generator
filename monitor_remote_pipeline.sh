#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
source env_set.sh

python3 monitor_remote_pipeline.py
