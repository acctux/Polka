#!/bin/bash
SESSION="nchat-session"
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" "nchat"
else
  echo "already exists"
fi
exec tmux attach -t "$SESSION"
