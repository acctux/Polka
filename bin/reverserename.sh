#!/bin/bash
OUTDIR="/home/nick/.local/mystuff/scripts/maimpdf/screens"

cd "$OUTDIR" || exit 1

# Get a sorted list of files by number
FILES=($(ls REG*.png 2>/dev/null | sort -V))

# Exit if no files
[ ${#FILES[@]} -eq 0 ] && echo "No REG files found." && exit 0

TOTAL=${#FILES[@]}

# Temporary folder to avoid overwrite
TMPDIR=$(mktemp -d)

for ((i=0; i<TOTAL; i++)); do
    OLD_FILE="${FILES[i]}"
    NEW_NUM=$((TOTAL - i))
    NEW_FILE=$(printf "REG%d.png" "$NEW_NUM")
    mv "$OLD_FILE" "$TMPDIR/$NEW_FILE"
done

# Move renamed files back
mv "$TMPDIR"/* .
rmdir "$TMPDIR"

echo "Reversed numbering for $TOTAL files."
