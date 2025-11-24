#!/usr/bin/env bash
set -euo pipefail

SESSION="music"
CAVA_WIDTH=25
FILES=("$@")
UEBERZUGCMD="ueberzugpp"

# --- Cleanup ---------------------------------------------
pkill -9 -x rmpc 2>/dev/null || true
pkill -9 -x "$UEBERZUGCMD" 2>/dev/null || true
tmux kill-session -t "$SESSION" 2>/dev/null || true

# --- Clear playlist, add files, play ---------------------
if [[ ${#FILES[@]} -gt 0 ]]; then
  mpc clear
  for f in "${FILES[@]}"; do
    mpc add "$f"
  done
  mpc play
fi

# --- Start new session ------------------------------------
tmux new-session -d -s "$SESSION" -x "$(tput cols)" -y "$(tput lines)" "bash -lc rmpc"
tmux split-window -h -p "$CAVA_WIDTH" -t "${SESSION}:0" "bash -lc cava"
tmux select-pane -t "${SESSION}:0.0"
tmux set-option -t "$SESSION" status off
exec tmux attach -t "$SESSION"
