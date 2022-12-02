#!/bin/bash
cd "$(dirname "$0")"
if [ `ping -c1 -W10 8.8.8.8 | grep '0 received' | wc -l` == "0" ]; then echo "on" > internet_state; else echo "off" > internet_state; fi
