layouts=("us" "ru" "ua")
state_file="${XDG_CACHE_HOME:-$HOME/.cache}/hypr_kb_layout_index"

mkdir -p "$(dirname "$state_file")"
current_index=0
[[ -f "$state_file" ]] && current_index=$(<"$state_file")

next_index=$(((current_index + 1) % ${#layouts[@]}))
next_layout="${layouts[$next_index]}"

hyprctl keyword input:kb_layout "$next_layout"
echo "$next_index" >"$state_file"

# Refresh Waybar immediately
