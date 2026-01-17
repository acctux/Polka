#!/bin/bash

if systemctl --user is-active --quiet mpd.service && sleep 0.1; then
  mpc toggle
else
  systemctl --user start mpd.service
  mpc play
  notify-send "MPD" "Started MPD"
fi
