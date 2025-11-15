#!/usr/bin/env bash

# Get the current layout code from hyprctl
current=$(sleep 0.1 && hyprctl getoption input:kb_layout | sed -n 's/^str: //p' | cut -d',' -f1 | head -n1)

# Map layout code to emoji
case "$current" in
us) echo "🇺🇸" ;;
ru) echo "🇷🇺" ;;
ua) echo "🇺🇦" ;;
*) echo "❓" ;;
esac
