#!/usr/bin/env bash

# Define the layouts in the cycle order
layouts=("us" "ru" "ua")

# Get the current keyboard layout as reported by Hyprland
current_layout=$(hyprctl getoption input:kb_layout -j | jq -r '.str' | cut -d',' -f1)

# Find the current layout index
for i in "${!layouts[@]}"; do
  if [[ "${layouts[$i]}" == "$current_layout" ]]; then
    current_index=$i
    break
  fi
done

# Default to 0 if no match found
current_index=${current_index:-0}

# Determine the next layout
next_index=$(((current_index + 1) % ${#layouts[@]}))
next_layout="${layouts[$next_index]}"

# Apply the next layout
hyprctl keyword input:kb_layout "$next_layout"
