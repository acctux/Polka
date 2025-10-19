#!/usr/bin/env bash
set -euo pipefail

H="$HOME"
LS="$H/.local/share"
C="$H/.config"
BACKUP_DIR="$HOME/Lit/newinstall/archives"
TB_DIR="$H/.thunderbird"
SYS_TAR="$BACKUP_DIR/system_backup.tar.gz"
TAR_FILE="$BACKUP_DIR/backup.tar.gz"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Debug: Print EXCLUDE_FILES
echo "DEBUG: EXCLUDE_FILES=" >&2
printf '%s\n' "${EXCLUDE_FILES[@]}" >&2

# Resolve Thunderbird profile
resolve_tb_profile() {
    local candidate
    for candidate in "$TB_DIR"/*.default*; do
        [[ -d "$candidate" ]] || continue
        local count
        count=$(find "$candidate" -mindepth 1 -maxdepth 1 | wc -l)
        if (( count > 5 )); then
            echo "$candidate"
            echo "DEBUG: Found Thunderbird profile: $candidate" >&2
            return 0
        fi
    done
    echo "No Thunderbird default profile found in $TB_DIR" >&2
    return 1
}

# Process a directory and return all files/directories
process_directory() {
    local dir="$1"
    echo "DEBUG: Processing directory: $dir" >&2
    find "$dir" \( -type f -o -type d \) -print0 | while IFS= read -r -d $'\0' f; do
        echo "DEBUG: Including from $dir: ${f#$HOME/}" >&2
        printf "%s\0" "${f#$HOME/}"
    done
}

# Prepare tar input list safely (returns null-separated paths)
prepare_tar_list() {
    local files=("$@")
    for path in "${files[@]}"; do
        if [[ -e "$path" ]]; then
            echo "DEBUG: Including top-level path: ${path#$HOME/}" >&2
            printf "%s\0" "${path#$HOME/}"  # print the file or dir itself
            if [[ -d "$path" ]]; then
                echo "DEBUG: Processing directory: ${path#$HOME/}" >&2
                process_directory "$path"
            fi
        else
            echo "Warning: $path does not exist, skipping" >&2
        fi
    done
}

backup_system_files() {
    sudo tar -C "$BACKUP_DIR" -czf "$SYS_TAR" "${SYS_FILES[@]}"
    # "$BACKUP_TAR" \ --exclude='etc/resolv.conf'"{SYS_FILES[@]}"
    # prepare_tar_list "${INCLUDE_FILES[@]}" | tar --null -czf "$TAR_FILE" -C "$HOME" -T -
    echo "System backup saved to $SYS_TAR"
}

main() {
    # Find Thunderbird profile
    local tb_profile
    tb_profile=$(resolve_tb_profile) || exit 1

    # Expand Thunderbird-specific files relative to profile
    local expanded_tb_files=()
    for f in "${TB_INCLUDE_FILES[@]}"; do
        expanded_tb_files+=("$tb_profile/$f")
    done

    # Merge with INCLUDE_FILES from config.sh
    local all_includes=("${INCLUDE_FILES[@]}" "${expanded_tb_files[@]}")
    echo "DEBUG: All included paths=" >&2
    printf '%s\n' "${all_includes[@]}" >&2

    # Build tar exclude arguments with relative paths
    local exclude_args=()
    for ex in "${EXCLUDE_FILES[@]}"; do
        exclude_args+=( --exclude="${ex#$HOME/}" )
    done
    echo "DEBUG: tar command: tar --null -czf \"$TAR_FILE\" -C \"$HOME\" ${exclude_args[*]} -T -" >&2

    # Create tarball with exclusions
    prepare_tar_list "${all_includes[@]}" | \
        tar --null -czf "$TAR_FILE" -C "$HOME" "${exclude_args[@]}" -T -
    echo "Backup saved to $TAR_FILE"
    backup_system_files
}

main
