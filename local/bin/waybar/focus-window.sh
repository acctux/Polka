#!/bin/bash

WINDOW_ADDRESS="$1"
MOUSE_BUTTON="$2"

case "$MOUSE_BUTTON" in
1)
  hyprctl dispatch focuswindow "address:$WINDOW_ADDRESS"
  ;;
2)
  PID=$(hyprctl clients -j | jq -r ".[] | select(.address == \"$WINDOW_ADDRESS\") | .pid")
  if [[ -n "$PID" && "$PID" != "null" ]]; then
    kill -9 "$PID"
  fi
  ;;
*)
  exit 0
  ;;
esac
