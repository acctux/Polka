#!/usr/bin/env bash

# Get the current layout code from hyprctl
current=$(hyprctl getoption input:kb_layout | grep '^str:' | awk '{print $2}')

# Map layout code to emoji
case "$current" in
us) echo "🇺🇸" ;;
ru) echo "🇷🇺" ;;
ua) echo "🇺🇦" ;;
*) echo "❓" ;;
esac
