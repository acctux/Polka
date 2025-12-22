#!/bin/sh
set -e
ZONEINFO=/usr/share/zoneinfo
ZONETAB="$ZONEINFO/zone1970.tab"
CURRENT_TZ=$(timedatectl show --property=Timezone --value)
TZONE=$(awk 'NF && $1 !~ /^#/ {print $3}' "$ZONETAB" | sort | fuzzel --dmenu --prompt="Timezone ($CURRENT_TZ): ")
[ -z "$TZONE" ] && exit 0
alacritty -e sudo timedatectl set-timezone "$TZONE"
