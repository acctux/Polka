WLOGOUT_LAYOUT="$HOME/.config/wlogout/layout"
CURRENT_ENTRY=$(bootctl status | grep "Current Entry:" | awk '{print $3}')
WLOGOUT_ENTRY=$(grep -i '"label" *: *"reboot"' -A1 "$HOME/.config/wlogout/layout" |
  grep -o 'boot-loader-entry=[^",]*' | cut -d= -f2 || true)

BOOT_NORMAL="arch.conf"
BOOT_BLACKLIST="arch-blacklist-nvidia.conf"

compare_boot_entries_json() {
  local icon=""

  case "$WLOGOUT_ENTRY" in
  "$BOOT_NORMAL")
    icon="󱓞"
    ;;
  "$BOOT_BLACKLIST")
    icon="󱙷"
    ;;
  esac

  if [[ "$WLOGOUT_ENTRY" == $CURRENT_ENTRY ]]; then
    echo "{\"text\": \"$icon\", \"tooltip\": \"Current: $CURRENT_ENTRY\\nNext: $WLOGOUT_ENTRY\"}"
  else
    icon="⚠️"
    echo "{\"text\": \"$icon\", \"tooltip\": \"Restart required.\\nNext reboot: $WLOGOUT_ENTRY\"}"
  fi
}

compare_boot_entries_json
