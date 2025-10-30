CURRENT_ENTRY=$(bootctl status | grep "Current Entry:" | awk '{print $3}')
WLOGOUT_ENTRY=$(grep -i 'reboot' "$WLOGOUT_LAYOUT" | grep -oP '--boot-loader-entry=\K[^''"[:space:]]+' | head -1 || true)
