#!/usr/bin/env bash
set -euo pipefail

SESSION="music"
CAVA_WIDTH=25
MUSIC_SERVICES=("mpd.service" "mpd-mpris.service")

existing_tmux() {
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

start_services() {
  for service in "${MUSIC_SERVICES[@]}"; do
    if systemctl --user is-active --quiet "$service"; then
      echo "$service already started."
    else
      echo "starting $service."
      systemctl --user start "$service"
    fi
  done
}

create_tmux_session() {
  tmux new-session -d -s "$SESSION" -x "$(tput cols)" -y "$(tput lines)" "rmpc"
  tmux split-window -h -p "$CAVA_WIDTH" -t "${SESSION}:0" "cava"
  tmux select-pane -t "${SESSION}:0.0"
  tmux set-option -t "$SESSION" status off
}

main() {
  if ! existing_tmux; then
    start_services
    create_tmux_session
  fi
  exec tmux attach -t "$SESSION"
}
main
