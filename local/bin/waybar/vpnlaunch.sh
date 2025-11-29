#!/bin/bash
CONFIG="$HOME/.config/Proton/VPN/app-config.json"
jq '.start_app_minimized=false' "$CONFIG" >/tmp/config.json
cp /tmp/config.json "$CONFIG"
protonvpn-app
