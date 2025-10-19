#!/usr/bin/env bash
#  _   _           _       _
# | | | |_ __   __| | __ _| |_ ___  ___
# | | | | '_ \ / _` |/ _` | __/ _ \/ __|
# | |_| | |_) | (_| | (_| | ||  __/\__ \
#  \___/| .__/ \__,_|\__,_|\__\___||___/
#       |_|
#

check_lock_files() {
  local pacman_lock="/var/lib/pacman/db.lck"
  local checkup_lock="${TMPDIR:-/tmp}/checkup-db-${UID}/db.lck"
  while [ -f "$pacman_lock" ] || [ -f "$checkup_lock" ]; do
    sleep 1
  done
}
check_lock_files
updates=$(paru -Qua | sort -u | wc -l) || updates=0

# Output in JSON format for Waybar Module custom-updates
if [ "$updates" -ge 100 ]; then
  printf '{"text": "%s", "alt": "%s", "tooltip": "Click to update your system"}' "$updates"
else
  printf '{}'
fi
