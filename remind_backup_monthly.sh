#!/bin/bash
cd "$(dirname "$0")"
python3 create_mail.py "It's a good time to review and backup all links to Google Drive" "" > /dev/null
