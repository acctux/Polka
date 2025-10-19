#!/bin/bash

# Favorite applications and actions
apps=(
  "Clipboard:app.getclipboard.Clipboard"
  "File Manager:system-file-manager"
  "TLP Performance:ibus-typing-booster"
)
choice=$({
  for app in "${apps[@]}"; do
    label="${app%%:*}"
    icon="${app##*:}"
    printf "%s\0icon\x1f%s\n" "$label" "$icon"
  done
} | fuzzel --dmenu --hide-prompt \
    --config /home/nick/.local/bin/waybar/menus-fuzzel.ini)

# Handle selection
case "$choice" in
    *Clipboard*) exec nwg-clipman ;;
    *File\ Manager*) exec nemo ;;
    *TLP\ Performance*) exec /home/nick/.local/bin/tlp/tlp.sh ;;
    *) exit 1 ;;
esac
