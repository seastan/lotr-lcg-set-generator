#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
python3 check_ringsdb_decks.py
