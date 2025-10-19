#!/bin/bash

image="$(pwd)/screen.png"

# Take screenshot silently without notification
spectacle --background --region --nonotify --output "$image" >/dev/null 2>&1

# Ensure file is written (Spectacle is async sometimes)
if [[ -f "$image" ]]; then
    # OCR with faster config (no auto language detection)
    tesseract "$image" - -l eng --psm 6 2>/dev/null | wl-copy
    rm -f "$image"
fi
