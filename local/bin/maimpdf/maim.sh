#!/bin/bash
OUTDIR="$HOME/.local/bin/maimpdf/screens"
REGION_FILE="$HOME/Polka/local/bin/maimpdf/region.txt"

# Load the saved region
if [[ ! -f "$REGION_FILE" ]]; then
  notify-send "No saved region found! Run the region selection script first."
  exit 1
fi
REGION=$(<"$REGION_FILE")

# Find the next available number
NUM=$(printf "%03d" $(($(ls "$OUTDIR" | grep -oP '^[0-9]+' | sort -n | tail -1 2>/dev/null || echo 0) + 1)))

FILENAME="$OUTDIR/$NUM.png"

# Take the screenshot using the saved region
grim -g "$REGION" "$FILENAME"
notify-send "Screenshot saved: $FILENAME"
