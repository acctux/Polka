#!/usr/bin/env bash
# ocr_walker_pipe.sh

CHOICE_1="OCR Screenshot"
CHOICE_2="Set Screenshot Region"
# Define menu options
MENU="$CHOICE_1\n$CHOICE_2\nCancel"

# Pipe options into walker in dmenu mode and capture selection
CHOICE=$(echo -e "$MENU" | walker --dmenu "OCR Action:")

case "$CHOICE" in
$CHOICE_1)
  bash /home/nick/Polka/local/bin/ocrcopy/ocrcopy.sh
  ;;
$CHOICE_2)
  bash /home/nick/Polka/local/bin/maimpdf/maimregion.sh
  ;;
"Cancel" | "")
  exit 0
  ;;
esac
