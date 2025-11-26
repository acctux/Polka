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

get_vivaldi_status() {
  player_status=$(playerctl status --player=vivaldi 2>/dev/null)
  if [ "$player_status" == "Paused" ]; then
    return 1
  fi
}

get_vivaldi_info() {
  artist=$(playerctl --player=vivaldi metadata xesam:artist 2>/dev/null)
  title=$(playerctl --player=vivaldi metadata xesam:title 2>/dev/null)
}

get_player_info() {
  player_status=$(playerctl status 2>/dev/null)
  if [[ $? -ne 0 || -z "$player_status" ]]; then
    rm -f "$SCROLL_FILE" "$MEDIA_FILE"
    exit 0
  fi
  if [ "$player_status" == "Stopped" ]; then
    artist=$(playerctl --player=vivaldi metadata xesam:artist 2>/dev/null)
    title=$(playerctl --player=vivaldi metadata xesam:title 2>/dev/null)
  else
    artist=$(playerctl metadata xesam:artist 2>/dev/null)
    title=$(playerctl metadata xesam:title 2>/dev/null)
  fi
}

create_track_string() {
  if [[ -z "$artist" && -z "$title" ]]; then
    return 1
  fi
  track="$title • $artist • "
  return 0
}

handle_scroll_position() {
  last_track=$(cat "$MEDIA_FILE" 2>/dev/null)
  if [[ "$track" != "$last_track" ]]; then
    echo "$track" >"$MEDIA_FILE"
    echo "0" >"$SCROLL_FILE"
    scroll_pos=0
  else
    scroll_pos=$(cat "$SCROLL_FILE" 2>/dev/null)
    [[ -z "$scroll_pos" ]] && scroll_pos=0
  fi
}

calculate_visible_length() {
  visible_chars=$((${#track} * 1 / 8))
  [[ $visible_chars -lt $VISIBLE_MIN ]] && visible_chars=$VISIBLE_MIN
}

update_scroll_position() {
  if [[ "$player_status" == "Paused" ]]; then
    return
  else
    scroll_pos=$((scroll_pos + 1))
    if ((scroll_pos > ${#track})); then
      sleep 2
      scroll_pos=0
    fi
    echo "$scroll_pos" >"$SCROLL_FILE"
  fi
}

create_scrolling_text() {
  if ((scroll_pos + visible_chars <= ${#track})); then
    display_text="${track:scroll_pos:visible_chars}"
  else
    wrap_len=$((scroll_pos + visible_chars - ${#track}))
    display_text="${track:scroll_pos}${track:0:wrap_len}"
  fi
}

output_json() {
  echo "{\"text\": \"$display_text\", \"class\": \"${player_status,,}\"}"
}

main() {
  if get_vivaldi_status; then
    get_vivaldi_info
  else
    get_player_info
  fi
  create_track_string
  handle_scroll_position
  calculate_visible_length
  update_scroll_position
  create_scrolling_text
  output_json
}
main
