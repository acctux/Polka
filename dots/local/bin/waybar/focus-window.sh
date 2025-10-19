
#!/bin/bash

# Arguments from Waybar
WINDOW_ADDRESS="$1"
MOUSE_BUTTON="$2"

# Optional: Only focus on left-click
if [[ "$MOUSE_BUTTON" != "1" ]]; then
    exit 0
fi

# Focus the window using hyprctl
hyprctl dispatch focuswindow "address:$WINDOW_ADDRESS"
