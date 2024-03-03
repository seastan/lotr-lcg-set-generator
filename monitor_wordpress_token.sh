#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
TOKEN=`grep -a wordpress_token mpc_monitor.json | sed -e 's/^\s* "wordpress_token": "//' -e 's/",$//'`
RES=`curl -G -s --data-urlencode "client_id=76623" --data-urlencode "token=$TOKEN" https://public-api.wordpress.com/oauth2/token-info | grep -a '"client_id":"76623"'`
if [[ ! "$RES" ]]; then
  python3 create_mail.py "Wordpress token might be expired: can't obtain the correct response from the server" "" > /dev/null
fi
