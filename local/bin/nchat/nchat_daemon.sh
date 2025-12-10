#!/bin/bash
SESSION="nchat"
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmuxp load -d "$SESSION"
fi
nchat --export /home/nick/Lit/docs/nchat
exec tmux attach -t "$SESSION"
