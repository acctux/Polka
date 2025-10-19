#!/bin/bash

# Define bases
HOME_BASE="/home/nick"
DOTFILES_BASE="/home/nick/Lit/dotfiles/Home"

# Wofi style file (reuse from previous)
STYLE_FILE="$HOME/.local/bin/wofi/fav_menu.css"

# Function to handle move and symlink for a single path
move_and_symlink() {
    local selected="$1"

    # Check if under home
    if [[ ! "$selected" == "$HOME_BASE"* ]]; then
        notify-send "Error" "Selected path must be under $HOME_BASE"
        return 1
    fi

    # Compute relative and new path
    local relative="${selected#$HOME_BASE/}"
    local new_path="$DOTFILES_BASE/$relative"
    local new_dir="$(dirname "$new_path")"

    # Check if already exists at new location
    if [[ -e "$new_path" ]]; then
        notify-send "Error" "Path already exists at $new_path"
        return 1
    fi

    # Create parent dirs if needed
    mkdir -p "$new_dir"

    # Move
    mv "$selected" "$new_path"

    # Symlink back
    ln -s "$new_path" "$selected"

    notify-send "Success" "Moved $selected to $new_path and created symlink"
}

# Get selected paths (%F is space-separated)
SELECTED_PATHS=("$@")

# If no selection, exit
if [ ${#SELECTED_PATHS[@]} -eq 0 ]; then
    notify-send "Error" "No file or folder selected"
    exit 1
fi

# Build description for confirmation
DESCRIPTION="Move and symlink the following to $DOTFILES_BASE equivalents:\n"
for path in "${SELECTED_PATHS[@]}"; do
    DESCRIPTION+="$(basename "$path")\n"
done
DESCRIPTION+="\nProceed?"

# Show Wofi confirmation menu
OPTIONS=("Yes" "No")
choice=$(printf "%s\n" "${OPTIONS[@]}" | wofi --dmenu --style "$STYLE_FILE" \
    --prompt "$DESCRIPTION" --width 400 --height 200 --location center --hide-scroll)

# Exit if No or nothing selected
if [[ "$choice" != "Yes" ]]; then
    exit 0
fi

# Process each selected path
for path in "${SELECTED_PATHS[@]}"; do
    move_and_symlink "$path"
done
