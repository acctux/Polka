#!/bin/bash
SESSION="rmpc"
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmuxp load -d "$SESSION"
else
  echo "already exists"
fi
exec tmux attach -t "$SESSION"
