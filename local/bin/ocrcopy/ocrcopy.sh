#!/bin/bash

image="$HOME/.cache/ocr_region.png"

# Remove existing file or directory
[ -e "$image" ] && rm -rf "$image"

# Capture a region screenshot silently with grim
grim -g "$(slurp)" "$image" >/dev/null 2>&1

# Ensure the image exists
if [[ -f "$image" ]]; then
  # Fast OCR using Tesseract (English only, no auto lang detection)
  tesseract "$image" - -l eng --psm 6 2>/dev/null | wl-copy
  # Clean up
  rm -f "$image"
else
  notify-send "OCR" "Screenshot failed"
fi
