#!/bin/bash

if systemctl --user is-active --quiet mpd.service; then
  mpc toggle
  notify-send "MPD" "Stopped MPD"
else
  systemctl --user start "$SERVICE"
  notify-send "MPD" "Started MPD"
fi
