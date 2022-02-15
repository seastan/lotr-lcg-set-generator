#!/bin/bash
cd "$(dirname "$0")"
./cron_log.sh | egrep -a ' ERROR: | INFO: Started: | INFO: Sheet Card Data changed| INFO: Sheet Scratch Data changed'
