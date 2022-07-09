#!/bin/bash
# 5 8 * * * flock -xn /home/webhost/python/AR/player_cards_stat.lock -c '/home/webhost/python/AR/player_cards_stat.sh'
cd "$(dirname "$0")"
python3 player_cards_stat.py
