#!/bin/bash
cd "$(dirname "$0")"
python3 create_mail.py "It's a good time to backup ALeP CardImages folder" "" > /dev/null
