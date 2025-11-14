#!/bin/bash

STATE_FILE="$HOME/.cache/hyprsunset_state"
PROFILE_DIR="$HOME/Polka/local/bin/hyprsunset"
ACTIVE_CONF="$HOME/.config/hypr/hyprsunset.conf"

# List profiles automatically
PROFILES=("$PROFILE_DIR"/*.conf)
MAX_INDEX=$(( ${#PROFILES[@]} - 1 ))

STATE=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

# Move to next profile
STATE=$(((STATE + 1) % (MAX_INDEX + 1)))

# Activate selected profile
cp "${PROFILES[$STATE]}" "$ACTIVE_CONF"
echo "$STATE" > "$STATE_FILE"

# Restart hyprsunset daemon
if ! systemctl --user restart hyprsunset.service; then
    killall hyprsunset
    systemctl --user stop hyprsunset.service
    systemctl --user start hyprsunset.service
fi


echo "Applied profile: $(basename "${PROFILES[$STATE]}")"

