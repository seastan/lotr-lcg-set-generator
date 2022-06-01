#!/bin/bash
cd "$(dirname "$0")"
SETIDS="$1"
if [[ ! "$SETIDS" ]]; then
  echo 'No set IDs specified'
  exit 1
fi
cd Renderer
node renderer.js "$SETIDS"
echo 'renderer.js finished'

export XDG_RUNTIME_DIR=/tmp
LOG_LEVEL=error

for filename in Output/portrait.*.html; do
    [ -e "$filename" ] || continue
    output=${filename//portrait\./}
    output=${output//\.html/.jpg}
    echo "Converting $filename to $output"
    /usr/local/bin/wkhtmltoimage --enable-local-file-access --images --enable-javascript --debug-javascript --javascript-delay 500 --no-stop-slow-scripts --log-level $LOG_LEVEL --disable-smart-width --width 429 --height 600 --format jpg --quality 95 "$filename" "$output"
    if [ -f "$output" ]; then
        rm $filename
    fi
done

for filename in Output/landscape.*.html; do
    [ -e "$filename" ] || continue
    output=${filename//landscape\./}
    output=${output//\.html/.jpg}
    echo "Converting $filename to $output"
    /usr/local/bin/wkhtmltoimage --enable-local-file-access --images --enable-javascript --debug-javascript --javascript-delay 500 --no-stop-slow-scripts --log-level $LOG_LEVEL --disable-smart-width --width 600 --height 429 --format jpg --quality 95 "$filename" "$output"
    if [ -f "$output" ]; then
        rm $filename
    fi
done

echo 'wkhtmltoimage finished'
cd ..
