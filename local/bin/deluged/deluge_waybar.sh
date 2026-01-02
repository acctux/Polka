#!/bin/bash

# Waybar custom module script to show  icon only when deluged.service is running
# Save this as e.g. ~/.config/waybar/scripts/deluge-status.sh
# Make it executable: chmod +x ~/.config/waybar/scripts/deluge-status.sh

ICON="" # Nerd Font icon for torrent/download (magnet symbol)

if systemctl --user is-active --quiet deluged.service 2>/dev/null ||
  systemctl is-active --quiet deluged.service 2>/dev/null; then
  # Service is running/active
  output='{
        "text": "'"$ICON"'",
        "tooltip": "Deluge daemon is running"
    }'
else
  # Service is not running – output empty text to hide the module
  output='{
        "text": "",
        "tooltip": "Deluge daemon is not running"
    }'
fi

echo "$output" | jq -c .
