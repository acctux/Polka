#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find all .sh files in the script's directory and subdirectories and make them executable
find "$SCRIPT_DIR" -type f -name "*.sh" | while read -r file; do
    chmod +x "$file"
    echo "Made executable: $file"
done
