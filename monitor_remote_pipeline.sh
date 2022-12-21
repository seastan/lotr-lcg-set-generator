#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 monitor_remote_pipeline.py
