#!/bin/bash

SERVICE="mpd.service"

# Check MPD status
if systemctl --user is-active --quiet "$SERVICE"; then
  systemctl --user stop "$SERVICE"
  notify-send "MPD" "Stopped MPD"
else
  systemctl --user start "$SERVICE"
  notify-send "MPD" "Started MPD"
fi
