#!/usr/bin/env sh

XBEL="$HOME/.local/share/user-places.xbel"
BOOKMARK="kdeconnect://4d76022a5910415f9073cc44af2025c3/"

if grep -q "$BOOKMARK" "$XBEL"; then
  notify-send "KDE Connect" "OnePlus bookmark detected"
fi
