#!/bin/bash
cd "$(dirname "$0")"
./cron_log.sh | egrep ' ERROR: | INFO: Started: '
