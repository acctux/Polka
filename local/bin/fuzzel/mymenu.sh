#!/usr/bin/env bash

CHOICE_1="OCR Screenshot"
CHOICE_2="Set Screenshot Region"
CHOICE_3="Screenshot Folder"
CHOICE_4="Start Youtube Daemon"
CHOICE_5="Stop Youtube Daemon"
CHOICE_6="Change Timezone"

MENU="$CHOICE_1
$CHOICE_2
$CHOICE_3
$CHOICE_4
$CHOICE_5
$CHOICE_6
Cancel"

CHOICE=$(printf "%s\n" "$MENU" | fuzzel --dmenu --hide-prompt --prompt="OCR Action:")

case "$CHOICE" in
"$CHOICE_1")
  bash /home/nick/Polka/local/bin/ocrcopy/ocrcopy.sh
  ;;
"$CHOICE_2")
  bash /home/nick/Polka/local/bin/maimpdf/maimregion.sh
  ;;
"$CHOICE_3")
  nemo /home/nick/Polka/local/bin/maimpdf/screens
  ;;
"$CHOICE_4")
  systemctl --user start mpvplay.service
  ;;
"$CHOICE_5")
  systemctl --user stop mpvplay.service
  ;;
"$CHOICE_6")
  ZONEINFO=/usr/share/zoneinfo
  ZONETAB="$ZONEINFO/zone1970.tab"
  CURRENT_TZ=$(timedatectl show --property=Timezone --value)
  TZONE=$(awk 'NF && $1 !~ /^#/ {print $3}' "$ZONETAB" | sort -u | fuzzel --dmenu --prompt="Timezone ($CURRENT_TZ): ")
  [ -n "$TZONE" ] && sudo timedatectl set-timezone "$TZONE"
  ;;
"Cancel" | "")
  exit 0
  ;;
esac
