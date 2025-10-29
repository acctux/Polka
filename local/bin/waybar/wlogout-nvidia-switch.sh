#!/usr/bin/env bash

set -euo pipefail

WLOGOUT_LAYOUT="$HOME/.config/wlogout/layout"
BOOT_NORMAL="arch.conf"
BOOT_BLACKLIST="arch-blacklist-nvidia.conf"

WLOGOUT_ENTRY=$(grep -i '"label" *: *"reboot"' -A1 "$WLOGOUT_LAYOUT" |
  grep -o 'boot-loader-entry=[^",]*' | cut -d= -f2 || true)

if [[ "$WLOGOUT_ENTRY" == "$BOOT_NORMAL" ]]; then
  NEW_ENTRY="$BOOT_BLACKLIST"
elif [[ "$WLOGOUT_ENTRY" == "$BOOT_BLACKLIST" ]]; then
  NEW_ENTRY="$BOOT_NORMAL"
else
  echo "[wlogout] Unknown current boot entry: $WLOGOUT_ENTRY" >&2
  exit 1
fi

sed -i "s|--boot-loader-entry=$WLOGOUT_ENTRY|--boot-loader-entry=$NEW_ENTRY|" "$WLOGOUT_LAYOUT"

echo "[wlogout] Replaced $WLOGOUT_ENTRY with $NEW_ENTRY in $WLOGOUT_LAYOUT"
