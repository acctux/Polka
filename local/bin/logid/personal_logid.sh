#!/usr/bin/env bash

DEVICE="MX Master 3S"
LOG="/tmp/logid.log"
ATTEMPTS=10

for i in $(seq 1 $ATTEMPTS); do
  sleep 3
  if grep -q "found: $DEVICE" "$LOG"; then
    break
  else
    sudo logid restart >"$LOG" 2>&1 &
    LOGID_PID=$!
  fi
done

if [ -n "$LOGID_PID" ]; then
  wait $LOGID_PID
fi
