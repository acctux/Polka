#!/usr/bin/env bash

FLAG_FILE="/tmp/mouse_connected.flag"

/usr/bin/solaar -w hide &
SOLLAAR_PID=$!
sleep 10
kill "$SOLLAAR_PID" 2>/dev/null
rm -f "$FLAG_FILE"
