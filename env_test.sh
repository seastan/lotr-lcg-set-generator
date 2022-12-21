#!/bin/bash
cd "$(dirname "$0")"

ENV_FILE="env_health_check.txt"
MAX_DIFF=43200

if [ -f "$ENV_FILE" ]; then
  let "DIFF = `date +%s` - `cat $ENV_FILE`"

  if (( $DIFF > $MAX_DIFF )); then
    exit 1
  else
    exit 0
  fi
else
  exit 1
fi
