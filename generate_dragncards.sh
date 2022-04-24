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

for filename in Output/portrait.*.html; do
    [ -e "$filename" ] || continue
    output=${filename//portrait\./}
    output=${output//\.html/.jpg}
    echo "Converting $filename to $output"
    # --debug-javascript
    /usr/local/bin/wkhtmltoimage --enable-javascript --enable-local-file-access --format jpg --images --javascript-delay 1000 --no-stop-slow-scripts --log-level error --quality 95 --width 429 --height 600 "$filename" "$output"
    if [ -f "$output" ]; then
        rm $filename
    fi
done

for filename in Output/landscape.*.html; do
    [ -e "$filename" ] || continue
    output=${filename//landscape\./}
    output=${output//\.html/.jpg}
    echo "Converting $filename to $output"
    # --debug-javascript
    /usr/local/bin/wkhtmltoimage --enable-javascript --enable-local-file-access --format jpg --images --javascript-delay 1000 --no-stop-slow-scripts --log-level error --quality 95 --width 600 --height 429 "$filename" "$output"
    if [ -f "$output" ]; then
        rm $filename
    fi
done

echo 'wkhtmltoimage finished'
cd ..
