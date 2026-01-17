#!/usr/bin/env bash

current=$(hyprctl devices -j | jq -r '.keyboards[] | select(.main == true) | .active_keymap' | grep -o '^\w\+' | head -n1)
case "$current" in
English) echo "🇺🇸" ;;
Russian) echo "🇷🇺" ;;
Ukrainian) echo "🇺🇦" ;;
*) echo "❓" ;;
esac
