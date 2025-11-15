#!/usr/bin/env bash

# --- Notifications ---
count=$(swaync-client -c 2>/dev/null || echo 0)
dnd=$(swaync-client -D 2>/dev/null || echo false)

if [[ "$count" -gt 0 ]]; then
  notif_icon=" 󱈸"
  notif_class="notif"
  if [[ "$dnd" == "true" ]]; then
    notif_icon=" 󰂠"
    notif_class="dnd"
  fi
else
  notif_icon=""
  notif_class="none"
fi

music_json=$("$HOME/Polka/local/bin/waybar/now-playing.sh" 2>/dev/null | tail -n1)

# Validate JSON (checks if it starts with `{`)
if [[ "$music_json" == \{* ]]; then
  # Extract the text safely
  music_text=$(echo "$music_json" | jq -r '.text // empty' 2>/dev/null)
else
  music_text=""
fi
# --- Combine ---
if [[ -n "$music_text" ]]; then
  # Append notification icon
  text="$notif_icon$music_text"
  alt="$music_text"
  main_class="music"
else
  # No music playing, show notifications only
  text="$notif_icon"
  alt="$notif_class"
  main_class="$notif_class"
fi

tooltip="Music: ${music_text:-None} | Notifications: ${count} | DND: ${dnd}"

# --- Output JSON for Waybar ---
jq -nc \
  --arg text "$text" \
  --arg alt "$alt" \
  --arg tooltip "$tooltip" \
  --arg class "$main_class" \
  '{text: $text, alt: $alt, tooltip: $tooltip, class: $class}'
