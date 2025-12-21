#!/bin/bash

LAST=""

while true; do
  CLIP=$(wl-paste --no-newline 2>/dev/null)
  if [[ "$CLIP" != "$LAST" ]]; then
    LAST="$CLIP"
    if [[ "$CLIP" =~ ^https?://(www\.)?youtube\.com/ ]] || [[ "$CLIP" =~ ^https?://youtu\.be/ ]]; then
      mpv "$CLIP" &
    fi
  fi
  sleep 3
done
