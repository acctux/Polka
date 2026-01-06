#!/usr/bin/env bash

CHOICE_1="OCR Screenshot"
CHOICE_2="Set Screenshot Region"
CHOICE_3="Screenshot Folder"
CHOICE_4="Start Youtube Daemon"
CHOICE_5="Stop Youtube Daemon"

MENU="$CHOICE_1
$CHOICE_2
$CHOICE_3
$CHOICE_4
$CHOICE_5
Cancel"

CHOICE=$(printf "%s\n" "$MENU" | fuzzel --dmenu --hide-prompt --prompt="OCR Action:")

case "$CHOICE" in
"$CHOICE_1")
  /home/nick/Polka/local/bin/ocr/ocrcopy.sh
  ;;
"$CHOICE_2")
  /home/nick/Polka/local/bin/ocr/maimregion.sh
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
"Cancel" | "")
  exit 0
  ;;
esac
