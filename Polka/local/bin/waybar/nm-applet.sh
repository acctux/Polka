#!/usr/bin/env bash
# Toggle nm-applet: kill if running, start if not

if pgrep -x nm-applet >/dev/null; then
  echo "nm-applet running — killing it..."
  pkill -x nm-applet
else
  echo "nm-applet not running — starting it..."
  nohup nm-applet --indicator >/dev/null 2>&1 &
fi
