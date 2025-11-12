#!/bin/bash

STATE_FILE="$HOME/.hyprsunset_state"
# Define 5 warmer (redder) temperatures
WARM_TEMPS=(6000 4500 2500 1000)
MAX_STEP=${#WARM_TEMPS[@]} # 5 steps

# Read the current state (0 = normal)
STATE=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

# Kill any existing hyprsunset process
if pgrep -x hyprsunset >/dev/null; then
  pkill -x hyprsunset
  sleep 0.2
fi

# Increment state and wrap around
STATE=$(((STATE + 1) % (MAX_STEP + 1))) # 0 → 1 → 2 ... → 5 → 0

if [[ "$STATE" -eq 0 ]]; then
  # Normal color
  hyprsunset --identity &
  echo "0" >"$STATE_FILE"
  echo "Restored normal color"
else
  # Apply the redder tone corresponding to the state
  TEMP=${WARM_TEMPS[$((STATE - 1))]}
  hyprsunset -t "$TEMP" &
  echo "$STATE" >"$STATE_FILE"
  echo "Applied warm tone: $TEMP K (step $STATE)"
fi
