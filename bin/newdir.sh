#!/usr/bin/env bash
set -euo pipefail

# Check for at least one folder argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <folder1> [folder2 ... folderN]"
    exit 1
fi

GROUP=gitaccess
USER="$(whoami)"

for DIR in "$@"; do
    if [ ! -d "$DIR" ]; then
        echo "Warning: Folder '$DIR' does not exist, skipping."
        continue
    fi

    echo "Processing '$DIR'..."
    # Directories: dr-xr-x--- with setgid
    sudo find "$DIR" -type d -exec chown "$USER:$GROUP" {} + -exec chmod 550 {} + -exec chmod g+s {} +

    # Files: rw-r----- owned by root
    sudo find "$DIR" -type f -exec chown root:$GROUP {} + -exec chmod 640 {} +

done
