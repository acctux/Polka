#!/usr/bin/env bash
set -euo pipefail

SESSION="music"
CAVA_WIDTH=30 # percentage of window width for cava pane

# find commands
RMPCCMD="$(command -v rmpc || true)"
CAVACMD="$(command -v cava || true)"

if [[ -z "$RMPCCMD" ]]; then
  echo "Error: rmpc not found on PATH. Install or add it to PATH."
  exit 1
fi
if [[ -z "$CAVACMD" ]]; then
  echo "Error: cava not found on PATH. Install or add it to PATH."
  exit 1
fi

# kill old session
tmux kill-session -t "$SESSION" 2>/dev/null || true

# start detached session with rmpc

tmux new-session -d -s "$SESSION" -x "$(tput cols)" -y "$(tput lines)" "bash -lc '$RMPCCMD'" \; \
  split-window -h -p "$CAVA_WIDTH" "bash -lc '$CAVACMD'" \; \
  select-pane -t 0 \; \
  set-option -g status off \; \
  attach-session -t "$SESSION"

sleep 0.1

# split horizontally and give cava the desired width
tmux split-window -h -p "$CAVA_WIDTH" -t "${SESSION}:0" "bash -lc '$CAVACMD'"

# focus on rmpc pane
tmux select-pane -t "${SESSION}:0.0"

# attach session
tmux attach-session -t "$SESSION"
