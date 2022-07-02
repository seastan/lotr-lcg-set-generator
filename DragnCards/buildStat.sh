#!/bin/bash
cd /var/www/dragncards.com/dragncards/frontend

if [ -f "current_run.txt" ]; then
  current_run="Current build started at $(cat current_run.txt). "
else
  current_run=""
fi

if [ -f "previous_run.txt" ]; then
  previous_run="Previous build: $(cat previous_run.txt)."
else
  previous_run="No previous builds."
fi

echo "$current_run$previous_run"