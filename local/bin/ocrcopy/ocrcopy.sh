#!/bin/bash

image="$HOME/.cache/ocr_region.png"

[ -e "$image" ] && rm -rf "$image"
grim -g "$(slurp)" "$image" >/dev/null 2>&1
if [[ -f "$image" ]]; then
  tesseract "$image" - -l eng --psm 6 2>/dev/null | wl-copy
  rm -f "$image"
else
  notify-send "OCR" "Screenshot failed"
fi
