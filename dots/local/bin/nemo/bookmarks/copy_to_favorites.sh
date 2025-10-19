#!/bin/bash

FAV_FILE="$HOME/.local/bin/nemo/bookmarks/nemo_favorites.txt"
BOOKMARKS_DIR="$HOME/.local/bin/bookmarks"
PATH_TO_ADD="$1"

# Ensure the bookmarks directory exists
mkdir -p "$BOOKMARKS_DIR"

# Create the favorites file if it doesn't exist
touch "$FAV_FILE"

# Add path to favorites file if not already present
if ! grep -Fxq "$PATH_TO_ADD" "$FAV_FILE"; then
    echo "$PATH_TO_ADD" >> "$FAV_FILE"
    notify-send "Added to favorites" "$PATH_TO_ADD"
else
    notify-send "Already in favorites" "$PATH_TO_ADD"
fi

# Create a symbolic link in the bookmarks directory
LINK_NAME="$(basename "$PATH_TO_ADD")"
LINK_PATH="$BOOKMARKS_DIR/$LINK_NAME"

# Avoid overwriting existing links
if [ ! -e "$LINK_PATH" ]; then
    ln -s "$PATH_TO_ADD" "$LINK_PATH"
else
    # Handle conflict: if the existing link points to the same place, do nothing
    if [ "$(readlink -f "$LINK_PATH")" != "$(readlink -f "$PATH_TO_ADD")" ]; then
        notify-send "Link conflict" "Bookmark '$LINK_NAME' already exists and points elsewhere."
    fi
fi
