#!/bin/bash
cd "$(dirname "$0")"
grep -s `date -d '1 days ago' '+%Y-%m-%d'` images_upload.log | grep -i error
