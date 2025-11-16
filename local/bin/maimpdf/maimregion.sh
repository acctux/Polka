#!/bin/bash
REGION_FILE="$HOME/Polka/local/bin/maimpdf/region.txt"

# Let user select a region
REGION=$(slurp)
echo "$REGION" >"$REGION_FILE"

echo "Region saved as: $REGION"
notify-send "Screenshot region saved"
