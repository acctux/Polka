#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 {batmode|default|none}"
  exit 1
fi

MODE="$1"

# Update TLP
sudo python3 /usr/local/bin/tlp.py "$MODE"

# Update Hyprland config
python3 /home/nick/Polka/local/bin/power/conf.py "$MODE"
