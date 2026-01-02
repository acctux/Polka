#!/usr/bin/env bash

CHOICE_1="Set Timer"
CHOICE_2="Change Timezone"

MENU="$CHOICE_1
$CHOICE_2
Cancel"

CHOICE=$(printf "%s\n" "$MENU" | fuzzel --dmenu --hide-prompt --config=/home/nick/.config/fuzzel/timemenu.ini)

case "$CHOICE" in
"$CHOICE_1")
  python "$HOME/Polka/local/bin/timer/set_timer.py"
  ;;
"$CHOICE_2")
  ZONEINFO=/usr/share/zoneinfo
  ZONETAB="$ZONEINFO/zone1970.tab"
  CURRENT_TZ=$(timedatectl show --property=Timezone --value)
  TZONE=$(awk 'NF && $1 !~ /^#/ {print $3}' "$ZONETAB" | sort -u |
    fuzzel --dmenu --prompt="Timezone ($CURRENT_TZ): ")
  if [ -n "$TZONE" ]; then
    alacritty -e sudo timedatectl set-timezone "$TZONE"
    pkill -SIGRTMIN+4 waybar
  fi
  ;;
"Cancel" | "")
  exit 0
  ;;
esac
