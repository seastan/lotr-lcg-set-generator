#!/bin/bash
cd "$(dirname "$0")"
python3 create_mail.py "It's a good time to backup the LotR folder to Google Drive and local hard drive" "" > /dev/null
