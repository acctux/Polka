#!/usr/bin/env bash

layouts=("us" "ru" "ua")
current_layout=$(hyprctl getoption input:kb_layout -j | jq -r '.str' | cut -d',' -f1)
for i in "${!layouts[@]}"; do
  if [[ "${layouts[$i]}" == "$current_layout" ]]; then
    current_index=$i
    break
  fi
done
current_index=${current_index:-0}
next_index=$(((current_index + 1) % ${#layouts[@]}))
next_layout="${layouts[$next_index]}"
hyprctl keyword input:kb_layout "$next_layout"
