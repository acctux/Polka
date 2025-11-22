#!/usr/bin/env bash
# ocr_walker_pipe.sh

CHOICE_1="OCR Screenshot"
CHOICE_2="Set Screenshot Region"
CHOICE_3="Screenshot Folder"
# Define menu options
MENU="$CHOICE_1\n$CHOICE_2\n$CHOICE_3\nCancel"

# Pipe options into walker in dmenu mode and capture selection
CHOICE=$(echo -e "$MENU" | walker --dmenu "OCR Action:")

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
"Cancel" | "")
  exit 0
  ;;
esac
