#!/usr/bin/env bash
set -euo pipefail

H="$HOME"
LS="$H/.local/share"
C="$H/.config"
E="/etc"

DOTFILES_DIR="$H/dotfiles"

SYS_FILES=(
    "$E/conf.d/wireless-regdom"
    "$E/firewalld/zones/block.xml"
    "$E/firewalld/firewalld.conf"
    "$E/iwd/main.conf"
    "$E/modprobe.d/wifi.conf"
    "$E/NetworkManager/conf.d/dns.conf"
    "$E/resolv.conf"
    "$E/dnsmasq.conf"
    "$E/dnsmasq-resolv.conf"
    "$E/resolvconf.conf"
    "$E/nsswitch.conf"
    "$E/chrony.conf"
#     "$E/polkit-1/rules.d/10-udisks2-mount.rules"
    "$E/makepkg.conf.d/99-parallel.conf"
    "$E/mkinitcpio.conf"
    "$E/mkinitcpio.d/linux.preset"
    "$E/ly/config.ini"
    "$E/ly/save.ini"
    "$E/conf.d/pacman-contrib"
    "$E/pacman.conf"
    "$E/paru.conf"
    "/boot/loader/loader.conf"
    "$H/.vimrc"
    "$H/.zshrc"
    "$H/.zsh_history"
    "$H/.gitconfig"
    "$LS/org.kde.syntax-highlighting"
    "$LS/recently-used.xbel"
    "$LS/user-places.xbel"
    "$C/arkrc"
    "$C/auroraerc"
    "$C/baloofilerc"
    "$C/dolphinrc"
    "$C/kalarmrc"
    "$C/kate-externaltoolspluginrc"
    "$C/katerc"
    "$C/katevirc"
    "$C/kcminputrc"
    "$C/kconf_updaterc"
    "$C/kdeglobals"
    "$C/kglobalshortcutsrc"
    "$C/kiorc"
    "$C/klipperrc"
    "$C/kmenueditrc"
    "$C/knightsrc"
    "$C/kscreenlockerrc"
    "$C/ksmserverrc"
    "$C/ksplashrc"
    "$C/kwinrc"
    "$C/kwinoutputconfig.json"
    "$C/mimeapps.list"
    "$C/okularpartrc"
    "$C/plasmarc"
    "$C/plasmashellrc"
    "$C/powerdevilrc"
    "$C/qBittorrent/qBittorrent.conf"
)


# This starts a for loop over all elements in the SYS_FILES array.
#
# "${SYS_FILES[@]}" ensures each array element is treated as a single item, even if the path contains spaces.
#
# file is the current element in the iteration — a path to a file or folder on your system.
for file in "${SYS_FILES[@]}"; do
    src="$file"
    dest="$DOTFILES_DIR${file/#$H/}"  # Replace $HOME with empty string for home files

    # Make sure parent directory exists
    mkdir -p "$(dirname "$dest")"

    # Copy the file into the repo
    cp -a "$src" "$dest"
    echo "Copied $src → $dest"
done

# find_thunderbird_profile() {
#     local TB_PRO_FILE="$1"   # Path to tb.txt
#     local TB_DIR="$2"        # Thunderbird profiles directory
#
#     # If profile file already exists, exit
#     if [ -e "$TB_PRO_FILE" ]; then
#         echo "DEBUG: Profile file already exists: $TB_PRO_FILE" >&2
#         return 0
#     fi
#
#     local candidate
#     for candidate in "$TB_DIR"/*.default*; do
#         # Skip if not a directory
#         [[ -d "$candidate" ]] || continue
#
#         # Count files/directories at top level
#         local count
#         count=$(find "$candidate" -mindepth 1 -maxdepth 1 | wc -l)
#
#         if (( count > 5 )); then
#             echo "$candidate" > "$TB_PRO_FILE"
#             echo "DEBUG: Found Thunderbird profile: $candidate" >&2
#             return 0
#         fi
#     done
#
#     echo "DEBUG: No suitable Thunderbird profile found in $TB_DIR" >&2
#     return 1
# }
# find_thunderbird_profile
#     fi
#     echo "No Thunderbird default profile found in $TB_DIR" >&2
#     return 1
# for FILE in "${FILES[@]}"; do
#     TARGET="$HOME/$FILE"
#
#     # Backup existing file
#     if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
#         mv "$TARGET" "$TARGET.backup"
#     fi
#
#     # Remove existing symlink
#
#     [ -L "$TARGET" ] && rm "$TARGET"
#
#     # Create symlink
#     ln -s "$SOURCE" "$TARGET"
#     echo "Linked $TARGET -> $SOURCE"
# done
#
#
#
# SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# source "$SCRIPT_DIR/config.sh"
#
# # Debug: Print EXCLUDE_FILES
# echo "DEBUG: EXCLUDE_FILES=" >&2
# printf '%s\n' "${EXCLUDE_FILES[@]}" >&2
#
# # Resolve Thunderbird profile
# resolve_tb_profile() {
#     if [ ! -e tb.txt ]; then
#             local candidate
#         for candidate in "$TB_DIR"/*.default*; do
#         [[ -d "$candidate" ]] || continue
#         local count
#         count=$(find "$candidate" -mindepth 1 -maxdepth 1 | wc -l)
#         if (( count > 5 )); then
#             echo "$candidate" > tb.txt
#             echo "DEBUG: Found Thunderbird profile: $candidate" >&2
#             return 0
#         fi
#     done
#
#     fi
#     echo "No Thunderbird default profile found in $TB_DIR" >&2
#     return 1
# }
#
# # Process a directory and return all files/directories
# process_directory() {
#     local dir="$1"
#     echo "DEBUG: Processing directory: $dir" >&2
#     find "$dir" \( -type f -o -type d \) -print0 | while IFS= read -r -d $'\0' f; do
#         echo "DEBUG: Including from $dir: ${f#$HOME/}" >&2
#         printf "%s\0" "${f#$HOME/}"
#     done
# }
#
# # Prepare tar input list safely (returns null-separated paths)
# prepare_tar_list() {
#     local files=("$@")
#     for path in "${files[@]}"; do
#         if [[ -e "$path" ]]; then
#             echo "DEBUG: Including top-level path: ${path#$HOME/}" >&2
#             printf "%s\0" "${path#$HOME/}"  # print the file or dir itself
#             if [[ -d "$path" ]]; then
#                 echo "DEBUG: Processing directory: ${path#$HOME/}" >&2
#                 process_directory "$path"
#             fi
#         else
#             echo "Warning: $path does not exist, skipping" >&2
#         fi
#     done
# }
#
# backup_system_files() {
#     sudo tar -C "$BACKUP_DIR" -czf "$SYS_TAR" "${SYS_FILES[@]}"
#     # "$BACKUP_TAR" \ --exclude='etc/resolv.conf'"{SYS_FILES[@]}"
#     # prepare_tar_list "${INCLUDE_FILES[@]}" | tar --null -czf "$TAR_FILE" -C "$HOME" -T -
#     echo "System backup saved to $SYS_TAR"
# }
# #!/usr/bin/env bash
# set -euo pipefail
#
# mv /home/nick/Lit/scripts/newdir/newdir.sh /home/nick/.config/systemd/user/newdir.sh
# # Check for at least one folder argument
# if [ $# -lt 1 ]; then
#     echo "Usage: $0 <folder1> [folder2 ... folderN]"
#     exit 1
# fi
#
# GROUP=gitaccess
# USER="$(whoami)"
#
# for DIR in "$@"; do
#     if [ ! -d "$DIR" ]; then
#         echo "Warning: Folder '$DIR' does not exist, skipping."
#         continue
#     fi
#
#     echo "Processing '$DIR'..."
#     # Directories: dr-xr-x--- with setgid
#     sudo find "$DIR" -type d -exec chown "$USER:$GROUP" {} + -exec chmod 550 {} + -exec chmod g+s {} +
#
#     # Files: rw-r----- owned by root
#     sudo find "$DIR" -type f -exec chown root:$GROUP {} + -exec chmod 640 {} +
#
# done
# mv /home/nick/.config/systemd/user/newdir.sh /home/nick/Lit/scripts/newdir/newdir.sh
#
# main() {
#     # Find Thunderbird profile
#     local tb_profile
#     tb_profile=$(resolve_tb_profile) || exit 1
#
#     # Expand Thunderbird-specific files relative to profile
#     local expanded_tb_files=()
#     for f in "${TB_INCLUDE_FILES[@]}"; do
#         expanded_tb_files+=("$tb_profile/$f")
#     done
#
#     # Merge with INCLUDE_FILES from config.sh
#     local all_includes=("${INCLUDE_FILES[@]}" "${expanded_tb_files[@]}")
#     echo "DEBUG: All included paths=" >&2
#     printf '%s\n' "${all_includes[@]}" >&2
#
#     # Build tar exclude arguments with relative paths
#     local exclude_args=()
#     for ex in "${EXCLUDE_FILES[@]}"; do
#         exclude_args+=( --exclude="${ex#$HOME/}" )
#     done
#     echo "DEBUG: tar command: tar --null -czf \"$TAR_FILE\" -C \"$HOME\" ${exclude_args[*]} -T -" >&2
#
#     # Create tarball with exclusions
#     prepare_tar_list "${all_includes[@]}" | \
#         tar --null -czf "$TAR_FILE" -C "$HOME" "${exclude_args[@]}" -T -
#     echo "Backup saved to $TAR_FILE"
#     backup_system_files
# }
#
# main

#     "$C/plasma-org.kde.plasma.desktop-appletsrc"
