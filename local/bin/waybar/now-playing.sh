#  /$$   /$$                               /$$$$$$$  /$$                     /$$
# | $$$ | $$                              | $$__  $$| $$                    |__/
# | $$$$| $$  /$$$$$$  /$$  /$$  /$$      | $$  \ $$| $$  /$$$$$$  /$$   /$$ /$$ /$$$$$$$   /$$$$$$
# | $$ $$ $$ /$$__  $$| $$ | $$ | $$      | $$$$$$$/| $$ |____  $$| $$  | $$| $$| $$__  $$ /$$__  $$
# | $$  $$$$| $$  \ $$| $$ | $$ | $$      | $$____/ | $$  /$$$$$$$| $$  | $$| $$| $$  \ $$| $$  \ $$
# | $$\  $$$| $$  | $$| $$ | $$ | $$      | $$      | $$ /$$__  $$| $$  | $$| $$| $$  | $$| $$  | $$
# | $$ \  $$|  $$$$$$/|  $$$$$/$$$$/      | $$      | $$|  $$$$$$$|  $$$$$$$| $$| $$  | $$|  $$$$$$$
# |__/  \__/ \______/  \_____/\___/       |__/      |__/ \_______/ \____  $$|__/|__/  |__/ \____  $$
#                                                                  /$$  | $$               /$$  \ $$
#                                                                 |  $$$$$$/              |  $$$$$$/
#                                                                  \______/                \______/
#___________________________________________________________________________________________________
# By Affan Mustafa 2025
#___________________________________________________________________________________________________

#!/bin/bash

VISIBLE_MIN=10
SCROLL_FILE="$HOME/.cache/nowplaying_scroll_pos"
MEDIA_FILE="$HOME/.cache/nowplaying_last_track"

# Fetch info
player_status=$(playerctl -a status 2>/dev/null | grep -i Playing | head -n1)
echo "Status: '$player_status'"
if [[ $? -ne 0 || -z "$player_status" ]]; then
  # No media player or not playing anything
  rm -f "$SCROLL_FILE" "$MEDIA_FILE"
  exit 0
fi

if [[ "$player_status" == "Paused" ]]; then
  # Do not advance scroll position
  echo ""
  exit 0
fi

artist=$(playerctl -a metadata xesam:artist 2>/dev/null | head -n1)
title=$(playerctl -a metadata xesam:title 2>/dev/null | head -n1)
[[ -z "$artist" && -z "$title" ]] && exit 0

track="•$title•$artist"

# Reset scroll if new track
last_track=$(cat "$MEDIA_FILE" 2>/dev/null)
if [[ "$track" != "$last_track" ]]; then
  echo "$track" >"$MEDIA_FILE"
  echo "0" >"$SCROLL_FILE"
  scroll_pos=0
else
  scroll_pos=$(cat "$SCROLL_FILE" 2>/dev/null)
  [[ -z "$scroll_pos" ]] && scroll_pos=0
fi

scroll_pos=$((scroll_pos + 4))
# Loop handling with 2s pause
if ((scroll_pos > ${#track})); then
  sleep 1
  scroll_pos=0
fi
echo "$scroll_pos" >"$SCROLL_FILE"

# Dynamic visible length
visible_chars=$((${#track} * 1 / 8))
[[ $visible_chars -lt $VISIBLE_MIN ]] && visible_chars=$VISIBLE_MIN

# Create scrolling text
if ((scroll_pos + visible_chars <= ${#track})); then
  display_text="${track:scroll_pos:visible_chars}"
else
  wrap_len=$((scroll_pos + visible_chars - ${#track}))
  display_text="${track:scroll_pos}${track:0:wrap_len}"
fi

# Output JSON for Waybar

safe_text=$(printf '%s' "$display_text" | jq -R .)
echo "{\"text\": $safe_text}"
