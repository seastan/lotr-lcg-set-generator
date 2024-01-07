#!/bin/bash
cd "$(dirname "$0")"

ENV_FILE="env_health_check.txt"
MAX_DIFF=43200

if [ -f "$ENV_FILE" ]; then
  CONTENT=`cat $ENV_FILE`
  if [ ! "$CONTENT" ]; then
    sleep 2
    CONTENT=`cat $ENV_FILE`
  fi

  if [ ! "$CONTENT" ]; then
    exit 1
  fi

  let "DIFF = `date +%s` - $CONTENT"

  if (( $DIFF > $MAX_DIFF )); then
    exit 1
  else
    exit 0
  fi
else
  exit 1
fi
