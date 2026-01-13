#!/bin/bash
REGION=$(slurp)
echo "$REGION" >"$HOME/Polka/local/bin/maimpdf/region.txt"
notify-send "Saved:$REGION"
