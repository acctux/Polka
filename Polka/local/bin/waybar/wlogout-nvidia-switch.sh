#!/usr/bin/env bash

WLOGOUT_LAYOUT="$HOME/.config/wlogout/layout"
BOOT_NORMAL="arch.conf"
BOOT_BLACKLIST="arch-blacklist-nvidia.conf"

WLOGOUT_ENTRY=$(grep -i '"label" *: *"reboot"' -A2 "$WLOGOUT_LAYOUT" |
  grep -oP 'boot-loader-entry=\K[^",]*' || true)

if [[ "$1" == "bios" ]]; then
  NEW_ACTION='systemctl reboot --firmware-setup'
elif [[ -z "$WLOGOUT_ENTRY" ]]; then
  NEW_ACTION="systemctl reboot --boot-loader-entry=$BOOT_NORMAL"
elif [[ "$WLOGOUT_ENTRY" == "$BOOT_NORMAL" ]]; then
  NEW_ACTION="systemctl reboot --boot-loader-entry=$BOOT_BLACKLIST"
elif [[ "$WLOGOUT_ENTRY" == "$BOOT_BLACKLIST" ]]; then
  NEW_ACTION="systemctl reboot --boot-loader-entry=$BOOT_NORMAL"
else
  echo "[wlogout] Unknown current boot entry: $WLOGOUT_ENTRY" >&2
  exit 1
fi

sed -i "/\"label\" *: *\"reboot\"/{n;s|\"action\" : \".*\"|\"action\" : \"$NEW_ACTION\"|}" "$WLOGOUT_LAYOUT"

echo "[wlogout] Updated reboot action to: $NEW_ACTION"
