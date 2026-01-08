#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 {batmode|default|none}"
  exit 1
fi
MODE="$1"
sudo python3 tlp.py "$MODE"
