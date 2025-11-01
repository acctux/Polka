#!/bin/bash
OUTDIR="/home/nick/.local/mystuff/Scripts/maimpdf/screens"

# Find the next available number
NUM=$(printf "%03d" $(( $(ls "$OUTDIR" | grep -oP '^[0-9]+' | sort -n | tail -1 2>/dev/null || echo 0) + 1 )))

FILENAME="$OUTDIR/$NUM.png"
REGION="644x467+569+199"

maim -g "$REGION" "$FILENAME"
notify-send "Screenshot saved: $FILENAME"
