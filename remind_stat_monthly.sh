#!/bin/bash
cd "$(dirname "$0")"
python3 create_mail.py "It's a good time to collect RingsDB and DragnCards statistics for the previous month" "" > /dev/null
