#!/usr/bin/env bash

CHOICE_1="OCR Screenshot"
CHOICE_2="Set Screenshot Region"
CHOICE_3="Screenshot Folder"
CHOICE_4="Start Youtube Daemon"
CHOICE_5="Stop Youtube Daemon"

MENU="$CHOICE_1\n$CHOICE_2\n$CHOICE_3\n$CHOICE_4\n$CHOICE_5\nCancel"

CHOICE=$(echo -e "$MENU" | fuzzel --dmenu "OCR Action:")
case "$CHOICE" in
$CHOICE_1)
  bash /home/nick/Polka/local/bin/ocrcopy/ocrcopy.sh
  ;;
$CHOICE_2)
  bash /home/nick/Polka/local/bin/maimpdf/maimregion.sh
  ;;
$CHOICE_3)
  nemo /home/nick/Polka/local/bin/maimpdf/screens
  ;;
$CHOICE_4)
  systemctl --user start mpvplay.service
  ;;
$CHOICE_5)
  systemctl --user stop mpvplay.service
  ;;
"Cancel" | "")
  exit 0
  ;;
esac
