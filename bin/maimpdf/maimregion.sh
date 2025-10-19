#!/bin/bash
REGION=$(slop)
echo "Region saved as: $REGION"

# Insert coordinates directly into screenshot script
sed -i "s|^REGION=.*|REGION=\"$REGION\"|" /home/nick/.local/mystuff/Scripts/maimpdf/maim.sh
