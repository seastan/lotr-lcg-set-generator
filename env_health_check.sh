#!/bin/bash
cd "$(dirname "$0")"
if (( `curl -sL -m 15 https://www.google.com | grep google | wc -l` > 0 )); then
  echo `date +%s` > env_health_check.txt
fi
