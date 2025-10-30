#!/usr/bin/env bash

DEVICE_ID="4d76022a5910415f9073cc44af2025c3"

# Default output
TOOLTIP="Device not reachable"
CLASS="disconnected"
COUNT_FILE="/tmp/waybar/kdecount.txt"

check_kdeconnect() {
  mkdir -p /tmp/waybar/
  if pgrep -x "kdeconnectd" >/dev/null; then
    if kdeconnect-cli -l 2>/dev/null | grep -q "$DEVICE_ID.*reachable"; then
      ICON=""
      TOOLTIP="Device reachable. Click to mount filesystem"
      CLASS="connected"
      echo "1" >"$COUNT_FILE"
    else
      TOOLTIP="Device is not reachable"
    fi
  else
    TOOLTIP="kdeconnectd is not running"
  fi
}

relay_info() {
  echo "{\"text\": \"$ICON\", \"tooltip\": \"$TOOLTIP\", \"class\": \"$CLASS\"}"
}

if [[ -f $COUNT_FILE ]]; then
  count=$(<"$COUNT_FILE")
  if ((count < 10)); then
    ((count++))
    echo "$count" >"$COUNT_FILE"
    ICON=""
    TOOLTIP="Device is reachable"
    CLASS="connected"
    relay_info
    exit 0
  fi
  rm "$COUNT_FILE"
fi
check_kdeconnect
relay_info
