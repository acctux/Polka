#!/bin/bash

STATE_FILE="$HOME/.hyprsunset_state"
WARM_TEMPS=(6000 3500 2000 1000)
MAX_STEP=${#WARM_TEMPS[@]}
STATE=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

if pgrep -x hyprsunset >/dev/null; then
  pkill -x hyprsunset
  sleep 0.2
fi

STATE=$(((STATE + 1) % (MAX_STEP + 1)))

if [[ "$STATE" -eq 0 ]]; then
  hyprsunset --identity &
  echo "0" >"$STATE_FILE"
  echo "Restored normal color"
else
  TEMP=${WARM_TEMPS[$((STATE - 1))]}
  hyprsunset -t "$TEMP" &
  echo "$STATE" >"$STATE_FILE"
  echo "Applied warm tone: $TEMP K (step $STATE)"
fi
