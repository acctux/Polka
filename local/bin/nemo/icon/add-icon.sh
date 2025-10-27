#!/bin/bash

# Check if at least one path is provided via %F
if [ $# -eq 0 ]; then
  echo "No directory selected"
  exit 1
fi

# Define your icons
icons=(
  "folder-images"
  "folder-documents"
  "folder-download"
  "folder-music"
  "folder-videos"
  "folder-github"
)

# Pass the list to fuzzel for fuzzy search
chosen_icon=$(printf '%s\n' "${icons[@]}" | fuzzel --dmenu --prompt "Select icon: ")

# Check if user selected something
if [ -z "$chosen_icon" ]; then
  echo "No icon selected"
  exit 1
fi

# Use the first selected path from %F
target_dir="$1"

# Verify that the target is a directory
if [ ! -d "$target_dir" ]; then
  echo "Error: '$target_dir' is not a directory"
  exit 1
fi

# Write the selected icon to a .directory file in the target directory
cat > "$target_dir/.directory" << EOF
[Desktop Entry]
Icon=$chosen_icon
EOF

# Check if the file was created successfully
if [ $? -eq 0 ]; then
  echo "Created .directory file in '$target_dir' with Icon=$chosen_icon"
else
  echo "Error: Failed to write .directory file in '$target_dir'"
  exit 1
fi
