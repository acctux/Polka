#!/usr/bin/env bash

current=$(sleep 0.1 && hyprctl getoption input:kb_layout | sed -n 's/^str: //p' | cut -d',' -f1 | head -n1)
case "$current" in
us) echo "🇺🇸" ;;
ru) echo "🇷🇺" ;;
ua) echo "🇺🇦" ;;
*) echo "❓" ;;
esac
