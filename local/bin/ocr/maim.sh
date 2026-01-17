#!/bin/bash
OUTDIR="$HOME/Documents/Pictures/maimpdf/screens"
REGION_FILE="$HOME/Polka/local/bin/ocr/region.txt"

mkdir -p "$OUTDIR"
if [[ ! -s "$REGION_FILE" ]]; then
  notify-send "No valid region saved! Run the region selection script first."
  exit 1
fi
read -r REGION <"$REGION_FILE"
last=$(fd -t f -e png . "$OUTDIR" |
  sd '.*/([0-9]{3})\.png' '$1' |
  sort -n |
  tail -1)
last=${last:-000}
NUM=$(printf "%03d" $((10#$last + 1)))
FILENAME="$OUTDIR/$NUM.png"
grim -g "$REGION" "$FILENAME"
notify-send "Saved"
