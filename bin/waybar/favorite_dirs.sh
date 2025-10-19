#!/bin/bash

# Favorites file
FAV_FILE="$HOME/.local/bin/nemo/bookmarks/nemo_favorites.txt"

# Exit if no favorites file exists or is empty
if [ ! -s "$FAV_FILE" ]; then
    notify-send "No favorites found" "Add some via Nemo context menu."
    exit 0
fi

# Create a temporary file to map display entries to full paths
MENU_FILE=$(mktemp)
MAP_FILE=$(mktemp)

while IFS= read -r folder_path; do
    [[ -z "$folder_path" ]] && continue

    # Always use folder name as display label
    display_name=$(basename "$folder_path")

    # Try to get icon from .directory file, fallback to "folder"
    dir_file="$folder_path/.directory"
    if [ -f "$dir_file" ]; then
        icon_name=$(grep "^Icon=" "$dir_file" | awk -F'=' '{print $2}' | xargs)
        [[ -z "$icon_name" ]] && icon_name="folder"
    else
        icon_name="folder"
    fi

    # Build menu entry
    printf "%s\0icon\x1f%s\n" "$display_name" "$icon_name" >> "$MENU_FILE"
    echo "$display_name|$folder_path" >> "$MAP_FILE"
done < "$FAV_FILE"

# Display the menu
choice_line=$(<"$MENU_FILE" fuzzel --dmenu --hide-prompt \
    --config /home/nick/.local/bin/waybar/menus-fuzzel.ini)

# Resolve selected folder path
selected_path=$(grep -F "${choice_line}|" "$MAP_FILE" | awk -F'|' '{print $2}')


# Clean up
rm "$MENU_FILE"

# Exit if nothing was selected
[[ -z "$choice_line" ]] && rm "$MAP_FILE" && exit 0

# Find the full path by matching the choice_line in the map
selected_path=$(grep "^$choice_line|" "$MAP_FILE" | awk -F'|' '{print $2}')

# Clean up the map file
rm "$MAP_FILE"

# Open the selected folder
exec nemo "$selected_path"
