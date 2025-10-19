#!/usr/bin/env bash
#    ____         __       ____               __     __
#   /  _/__  ___ / /____ _/ / / __ _____  ___/ /__ _/ /____ ___
#  _/ // _ \(_-</ __/ _ `/ / / / // / _ \/ _  / _ `/ __/ -_|_-<
# /___/_//_/___/\__/\_,_/_/_/  \_,_/ .__/\_,_/\_,_/\__/\__/___/
#                                 /_/

# Display potential package updates
echo ":: Checking for package updates..."
updates=$(paru -Qu)
if [ -z "$updates" ]; then
    echo "No updates available."
else
    echo "Available updates:"
    echo "$updates"
    echo
fi

# Confirm update
if gum confirm "DO YOU WANT TO START THE UPDATE NOW?"; then
    echo
    echo ":: Update started..."
    if paru -Syu --noconfirm; then
        # Reload Waybar if running
        if pgrep waybar &> /dev/null; then
            pkill -RTMIN+1 waybar
            echo ":: Waybar reloaded."
        fi
        echo ":: Update complete! Press [ENTER] to close."
    else
        echo ":: Update failed. Check logs for details."
        echo "Press [ENTER] to close."
    fi
    read
elif [ $? -eq 130 ]; then
    exit 130
else
    echo
    echo ":: Update canceled."
    exit
fi
