#!/usr/bin/env bash
set -euo pipefail

H="$HOME"
LS="$H/.local/share"
C="$H/.config"
DOTFILES_DIR="$H/Lit/dotfiles"

# Map directories to their subdirectory exclusions
declare -A EXCLUDE_MAP=(
    ["$LS/Anki2"]="User 1"
    ["$LS/klipper"]="data"
    ["$LS/lutris"]="runtime"
    ["$LS/plasma"]="look-and-feel"
)

copy_dir() {
    local src_dir="$1"
    local dest_dir="$2"
    local exclude_pattern="$3"

    if [[ ! -d "$src_dir" ]]; then
        echo "Warning: $src_dir does not exist, skipping."
        return
    fi

    mkdir -p "$dest_dir"

    if [[ -n "$exclude_pattern" ]]; then
        # Copy everything except the excluded subdirectory
        find "$src_dir" -mindepth 1 -maxdepth 1 ! -path "$src_dir/$exclude_pattern" \
            -exec cp -r --no-preserve=mode,ownership {} "$dest_dir/" \;
    else
        cp -r --no-preserve=mode,ownership "$src_dir/." "$dest_dir/"
    fi

    echo "Copied $src_dir → $dest_dir"
}

for src_dir in "${!EXCLUDE_MAP[@]}"; do
    # Make path relative to home for consistent storage
    relative="${src_dir/#$H/home}"
    dest_dir="$DOTFILES_DIR/$relative"

    copy_dir "$src_dir" "$dest_dir" "${EXCLUDE_MAP[$src_dir]}"
done
