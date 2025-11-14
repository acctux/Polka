#!/bin/bash

PROFILE_FILE="$HOME/Polka/local/bin/hyprsunset/3-1000.conf"
ACTIVE_CONF="$HOME/.config/hypr/hyprsunset.conf"

# Copy default profile (index 0)
cp "$PROFILE_FILE" "$ACTIVE_CONF"

# Restart hyprsunset daemon
if ! systemctl --user restart hyprsunset.service; then
    killall hyprsunset
    systemctl --user stop hyprsunset.service
    systemctl --user start hyprsunset.service
fi

echo "Default hyprsunset profile restored (9 PM timer)"

