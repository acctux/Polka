#!/usr/bin/env bash
set -euo pipefail

H="$HOME"
LS="$H/.local/share"
C="$H/.config"
E="/etc"
DOTFILES_DIR="$H/Lit/dotfiles"

# List of files and directories to copy
SYS_FILES=(
    # Home config folders
    "$C/alacritty"
    "$C/autostart"
    "$C/btop"
    "$C/feathernotes"
    "$C/firewall"
    "$C/GIMP"
    "$C/gtk-3.0"
    "$C/gtk-4.0"
    "$C/Kvantum"
    "$C/menus"
    "$C/octopi"
    "$C/qalculate"
    "$C/solaar"
    "$C/systemd"
    "$C/vlc"
    "$C/xsettingsd"
    "$C/kalarmresources"

    # Local share folders
    "$LS/applications"
    "$LS/aurorae"
    "$LS/color-schemes"
    "$LS/fonts"
    "$LS/kalarm"
    "$LS/desktop-directories"
    "$LS/org.kde.syntax-highlighting"
    "$LS/DBeaverData/workspace6"

    # System file
    "$E/sudoers.d/backupsudo"
)

for file in "${SYS_FILES[@]}"; do
    src="$file"  # The source path on the system (file or folder)

    if [[ "$file" == $H/* ]]; then
        dest="$DOTFILES_DIR${file/#$H/}"
        SUDO=""  # No sudo needed for home files
    else
        dest="$DOTFILES_DIR$src"
        SUDO="sudo"  # Use sudo because system files usually require root
    fi

    $SUDO mkdir -p "$(dirname "$dest")"

    if [ -d "$src" ]; then
        $SUDO cp -a "$src" "$dest"
    else
        $SUDO cp -a "$src" "$dest"
    fi

    echo "Copied $src → $dest"
done
