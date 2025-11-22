#!/bin/bash
OUTDIR="$HOME/.local/bin/maimpdf/screens"
REGION_FILE="$HOME/Polka/local/bin/maimpdf/region.txt"

# Ensure output directory exists
mkdir -p "$OUTDIR"

# Load saved region
if [[ ! -s "$REGION_FILE" ]]; then
    notify-send "No valid region saved! Run the region selection script first."
    exit 1
fi
read -r REGION < "$REGION_FILE"

# Determine next index using fd + sd
last=$(fd -t f -e png . "$OUTDIR" \
       | sd '.*/([0-9]{3})\.png' '$1' \
       | sort -n \
       | tail -1)

last=${last:-000}
NUM=$(printf "%03d" $((10#$last + 1)))

FILENAME="$OUTDIR/$NUM.png"

# Take screenshot
grim -g "$REGION" "$FILENAME"

notify-send "Saved screenshot: $FILENAME"

